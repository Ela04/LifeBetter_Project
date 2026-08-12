# src/apps/payments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.urls import reverse
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from transbank.error.transaction_create_error import TransactionCreateError
from transbank.error.transbank_error import TransbankError

from apps.expenses.models import ExpenseBill
from .models import TransbankTransaction
from .services import TransbankService


class InitiatePaymentView(LoginRequiredMixin, View):
    """
    Vista que procesa la intención de pago del residente y lo redirige a Transbank.
    """
    def post(self, request, bill_id):
        bill = get_object_or_404(ExpenseBill, id=bill_id, department__resident=request.user)
        
        if bill.status == ExpenseBill.Status.PAID:
            return redirect('dashboard')

        tbk_service = TransbankService()
        return_url = request.build_absolute_uri(reverse('payments:webpay_return'))

        # Captura segura de errores de red y API
        try:
            response, buy_order, session_id = tbk_service.create_transaction(bill, return_url)
        except (TransactionCreateError, TransbankError) as e:
            return render(request, 'payments/payment_failed.html', {
                'error': f'Rechazo en la pasarela de Transbank: {str(e)}'
            })
        except Exception as e:
            return render(request, 'payments/payment_failed.html', {
                'error': 'Error de conexión temporal con los servidores de Transbank. Por favor presiona reintentar.'
            })

        # Registro de intento de transacción
        TransbankTransaction.objects.create(
            bill=bill,
            buy_order=buy_order,
            session_id=session_id,
            tbk_token=response['token'],
            amount=bill.calculated_amount
        )

        # Redirección automática hacia Webpay Plus
        return render(request, 'payments/webpay_redirect.html', {
            'url': response['url'],
            'token': response['token']
        })


class WebpayReturnView(View):
    """
    Webhook / Callback al cual Transbank retorna después de que el usuario ingresa sus llaves/tarjeta.
    """
    def get(self, request):
        token = request.GET.get('token_ws')
        
        # Caso de cancelación por parte del usuario en Webpay
        if not token:
            tbk_token_cancelled = request.POST.get('TBK_TOKEN')
            if tbk_token_cancelled:
                TransbankTransaction.objects.filter(tbk_token=tbk_token_cancelled).update(
                    status=TransbankTransaction.TransactionStatus.FAILED
                )
            return render(request, 'payments/payment_failed.html', {
                'error': 'Operación cancelada por el usuario en el portal de pago.'
            })

        tbk_service = TransbankService()
        
        try:
            result = tbk_service.commit_transaction(token)
        except Exception as e:
            return render(request, 'payments/payment_failed.html', {
                'error': f'Error al confirmar la transacción con el banco: {str(e)}'
            })

        tx_record = get_object_or_404(TransbankTransaction, tbk_token=token)

        # Validar si el pago fue aprobado por el banco emisor
        if result.get('status') == 'AUTHORIZED' and result.get('response_code') == 0:
            with transaction.atomic():
                tx_record.status = TransbankTransaction.TransactionStatus.AUTHORIZED
                tx_record.authorization_code = result.get('authorization_code')
                tx_record.response_code = result.get('response_code')
                tx_record.payment_type_code = result.get('payment_type_code')
                tx_record.shares_number = result.get('shares_number', 0)
                tx_record.save()

                # Marcar la boleta del gasto común como PAGADA
                bill = tx_record.bill
                bill.status = ExpenseBill.Status.PAID
                bill.save()

            return render(request, 'payments/payment_success.html', {
                'transaction': tx_record, 
                'result': result
            })
        else:
            tx_record.status = TransbankTransaction.TransactionStatus.FAILED
            tx_record.response_code = result.get('response_code')
            tx_record.save()
            return render(request, 'payments/payment_failed.html', {
                'error': 'Transacción rechazada por la entidad bancaria.'
            })