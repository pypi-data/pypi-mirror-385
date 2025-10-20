import logging
from datetime import timedelta
from django.db import transaction
from django.dispatch import receiver
from django.http import Http404
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_scopes import scopes_disabled
from pretix.base.models import Order, OrderPayment, Quota
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import (
    logentry_display,
    periodic_task,
    register_payment_providers,
)

import pretix_xpay.xpay_api as xpay
from pretix_xpay.constants import (
    XPAY_RESULT_AUTHORIZED,
    XPAY_RESULT_CANCELED,
    XPAY_RESULT_CAPTURED,
    XPAY_RESULT_PENDING,
    XPAY_RESULT_REFUNDED,
)
from pretix_xpay.payment import XPayPaymentProvider
from pretix_xpay.utils import OrderStatus, get_settings_object, send_refund_needed_email

logger = logging.getLogger(__name__)


@receiver(register_payment_providers, dispatch_uid="payment_xpay")
def register_payment_provider(sender, **kwargs):
    return [XPayPaymentProvider]


@receiver(signal=logentry_display, dispatch_uid="xpay_logentry_display")
def pretixcontrol_logentry_display(sender, logentry, **kwargs):
    if not logentry.action_type.startswith("pretix_xpay.event"):
        return
    return _("XPay reported an event (Status {status}).").format(
        status=logentry.parsed_data.get("STATUS", "?")
    )


@receiver(periodic_task, dispatch_uid="payment_xpay_periodic_poll")
@scopes_disabled()
def poll_pending_payments(sender, **kwargs):
    logger.info("XPAY_poll_pending_payments: Running runperiodic")
    for payment in OrderPayment.objects.filter(
        provider="xpay",
        state__in=[
            OrderPayment.PAYMENT_STATE_PENDING,
            OrderPayment.PAYMENT_STATE_CREATED,
            OrderPayment.PAYMENT_STATE_CANCELED,
        ],
    ):
        settings = get_settings_object(payment.order.event)
        mins = (
            int(settings.poll_pending_timeout) if settings.poll_pending_timeout else 60
        )

        # We need to process even confirmed payments to find if someone has paid two times and make the order overpaid
        # if payment.order.status != Order.STATUS_EXPIRED and payment.order.status != Order.STATUS_PENDING:
        #    continue

        try:
            provider = payment.payment_provider
            data: OrderStatus = xpay.get_order_status(
                payment=payment, provider=provider
            )
            try:
                data.updatePaymentInformation(payment, provider)
            except Exception as e:
                logger.warning(
                    f"XPAY_poll_pending_payments [{payment.full_id}]: Exception in updating payment info: {repr(e)}"
                )

            if data.status in XPAY_RESULT_AUTHORIZED:
                xpay.confirm_payment_and_capture_from_preauth(
                    payment, provider, payment.order
                )

            elif data.status in XPAY_RESULT_CAPTURED:
                try:
                    payment.confirm()
                    logger.info(
                        f"XPAY_poll_pending_payments [{payment.full_id}]: Payment confirmed with status {data.status}"
                    )
                except Quota.QuotaExceededException:
                    logger.info(
                        f"XPAY_poll_pending_payments [{payment.full_id}]: Canceling payment quota was exceeded"
                    )
                    send_refund_needed_email(
                        payment, origin="periodic_task.poll_pending_payments"
                    )

            elif data.status in XPAY_RESULT_PENDING:
                # If the payment it's still pending, weep waiting
                if payment.state == OrderPayment.PAYMENT_STATE_CREATED:
                    with transaction.atomic():
                        logger.info(
                            f"XPAY_poll_pending_payments [{payment.full_id}]: Payment is now pending"
                        )
                        payment.state = OrderPayment.PAYMENT_STATE_PENDING
                        payment.save(update_fields=["state"])

            elif (
                data.status in XPAY_RESULT_REFUNDED
                or data.status in XPAY_RESULT_CANCELED
            ):
                logger.info(
                    f"XPAY_poll_pending_payments [{payment.full_id}]: Failing payment because found in a refunded or canceled status: {data.status}"
                )
                payment.fail(
                    info={"error": str(_("Payment in refund or canceled state"))}
                )

            else:
                logger.exception(
                    f"XPAY_poll_pending_payments [{payment.full_id}]: Unrecognized payment status: {data.status}"
                )

        except Http404 as e:
            if (
                payment.order.status == Order.STATUS_EXPIRED
                and payment.created < now() - timedelta(minutes=mins)
            ):
                logger.exception(
                    f"XPAY_poll_pending_payments [{payment.full_id}]: "
                    "Setting payment status to fail due to expired order and poll_pending_timeout reached: ",
                    e,
                )
                payment.fail(log_data={"result": "poll_timeout"})

        except Exception as e:
            logger.exception(
                f"XPAY_poll_pending_payments [{payment.full_id}]: Exception in polling transaction status: {repr(e)}"
            )


settings_hierarkey.add_default("payment_xpay_hash", "sha1", str)
settings_hierarkey.add_default("poll_pending_timeout", 60, int)
settings_hierarkey.add_default("enable_test_endpoints", False, bool)
