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
    Incluye resiliencia de socket y sanitización de parámetros.
    """
    def __init__(self):
        if settings.DEBUG:
            # Credenciales oficiales de prueba e integración
            self.tx = Transaction(WebpayOptions(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY,
                integration_type=IntegrationType.TEST
            ))
        else:
            # Credenciales de producción inyectadas desde .env
            self.tx = Transaction(WebpayOptions(
                commerce_code=settings.TRANSBANK_COMMERCE_CODE,
                api_key=settings.TRANSBANK_API_KEY,
                integration_type=IntegrationType.LIVE
            ))

    def create_transaction(self, bill, return_url: str):
        """
        Genera y valida la orden de compra antes de llamar a la API de Webpay.
        Garantiza parámetros estrictamente alfanuméricos.
        """
        # 1. buy_order estrictamente alfanumérico (máximo 26 caracteres)
        buy_order = f"O{uuid.uuid4().hex[:18].upper()}"

        # 2. session_id estrictamente alfanumérico (máximo 61 caracteres)
        session_id = f"S{bill.department.id}{uuid.uuid4().hex[:12].upper()}"

        # 3. Monto en enteros para Pesos Chilenos (CLP)
        amount = int(math.ceil(bill.calculated_amount))

        logger.info(f"Iniciando Tx Webpay: buy_order={buy_order}, amount={amount}")

        # 4. Solicitud al SDK de Transbank
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
        except Exception as e:
            logger.error(f"Error de Socket/Red al conectar con Transbank: {str(e)}")
            raise e

    def commit_transaction(self, token: str):
        """
        Confirma la transacción con el token enviado por Webpay en el retorno.
        """
        return self.tx.commit(token=token)