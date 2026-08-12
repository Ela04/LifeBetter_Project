import uuid
import math
import logging
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
from transbank.error.transbank_error import TransbankError
from transbank.error.transaction_create_error import TransactionCreateError

logger = logging.getLogger(__name__)


class TransbankService:
    """
    Servicio desacoplado para la integración con Transbank Webpay Plus SDK.
    """
    def __init__(self):
        # Leemos el entorno de forma segura
        commerce_code = getattr(settings, 'TRANSBANK_COMMERCE_CODE', IntegrationCommerceCodes.WEBPAY_PLUS)
        api_key = getattr(settings, 'TRANSBANK_API_KEY', IntegrationApiKeys.WEBPAY)

        # Si estamos en modo DEBUG o usando credenciales de prueba
        if getattr(settings, 'DEBUG', True) or commerce_code == IntegrationCommerceCodes.WEBPAY_PLUS:
            self.tx = Transaction(WebpayOptions(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY,
                integration_type=IntegrationType.TEST
            ))
        else:
            self.tx = Transaction(WebpayOptions(
                commerce_code=commerce_code,
                api_key=api_key,
                integration_type=IntegrationType.LIVE
            ))

    def create_transaction(self, bill, return_url: str):
        """
        Genera y valida la orden de compra antes de llamar a la API de Webpay.
        """
        buy_order = f"O{uuid.uuid4().hex[:18].upper()}"
        session_id = f"S{bill.department.id}{uuid.uuid4().hex[:12].upper()}"
        amount = int(math.ceil(bill.calculated_amount))

        try:
            response = self.tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )
            return response, buy_order, session_id
        except (TransactionCreateError, TransbankError) as e:
            logger.error(f"Error SDK Transbank: {str(e)}")
            raise e

    def commit_transaction(self, token: str):
        """
        Confirma la transacción con el token enviado por Webpay en el retorno.
        """
        return self.tx.commit(token=token)