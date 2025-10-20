TEST_URL = "https://int-ecommerce.nexi.it/ecomm/"
PROD_URL = "https://ecommerce.nexi.it/ecomm/"

ENDPOINT_ORDERS_CREATE = "ecomm/DispatcherServlet"
ENDPOINT_ORDERS_CONFIRM = "api/bo/contabilizza"
ENDPOINT_ORDERS_CANCEL = "api/bo/storna"
ENDPOINT_ORDERS_REFUND = "api/bo/storna"
ENDPOINT_ORDERS_STATUS = "api/bo/situazioneOrdine"

DOCS_TEST_CARDS_URL = "https://ecommerce.nexi.it/area-test"

HASH_TAG = "plugins:pretix_xpay"

XPAY_STATUS_SUCCESS = ["OK"]
XPAY_STATUS_FAILS = ["KO", "ANNULLO", "ERRORE"]
XPAY_STATUS_PENDING = ["PEN"]

XPAY_RESULT_AUTHORIZED = ["Autorizzato"]
XPAY_RESULT_CAPTURED = [
    "Contabilizzato",
    "In attesa di contab.",
    "Contabilizzato Parz.",
]
XPAY_RESULT_PENDING = ["In Corso", "Pendente"]
XPAY_RESULT_REFUNDED = [
    "Rimborsato",
    "Rimborsato Parz.",
    "In attesa di storno",
    "Stornato",
]
XPAY_RESULT_CANCELED = [
    "Autor. Negata",
    "Non Creato",
    "Negato",
    "Non valido",
    "Non generato",
    "Chiuso da backoffice",
    "Annullato",
    "Sospeso",
    "Storno Negato",
    "Storno Annullato",
]

XPAY_OPERATION_CAPTURE = "CONTAB."
XPAY_OPERATION_REFUND = "STORNO"

# Table of supported languages by XPay: https://ecommerce.nexi.it/specifiche-tecniche/tabelleecodifiche/codificalanguageid.html
LANGUAGE_DEFAULT = "ENG"
LANGUAGES_TRANSLATION = {
    "it": "ITA",
    "en": "ENG",
    "es": "SPA",
    "fr": "FRA",
    "de": "GER",
    "jp": "JPN",
    "cn": "CHI",
    "zh": "CHI",
    "ar": "ARA",
    "ru": "RUS",
    "pt": "POR",
}
