# src/apps/payments/services.py
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
    Servicio desacoplado para la integración con Transbank Webpay Plus SDK v4+.
    Garantiza la inyección correcta de WebpayOptions y parámetros sanitizados.
    """
    def __init__(self):
        commerce_code = getattr(settings, 'TRANSBANK_COMMERCE_CODE', IntegrationCommerceCodes.WEBPAY_PLUS)
        api_key = getattr(settings, 'TRANSBANK_API_KEY', IntegrationApiKeys.WEBPAY)

        # Transbank SDK v4+ exige pasar WebpayOptions al constructor de Transaction
        if getattr(settings, 'DEBUG', True) or commerce_code == IntegrationCommerceCodes.WEBPAY_PLUS:
            options = WebpayOptions(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY,
                integration_type=IntegrationType.TEST
            )
        else:
            options = WebpayOptions(
                commerce_code=commerce_code,
                api_key=api_key,
                integration_type=IntegrationType.LIVE
            )
        
        self.tx = Transaction(options=options)

    def create_transaction(self, bill, return_url: str):
        """
        Inicia la transacción garantizando buy_order alfanumérico (máx 26 caracteres)
        y monto entero para pesos chilenos (CLP).
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
        Confirma la transacción recibida desde el retorno de Webpay.
        """
        return self.tx.commit(token=token)