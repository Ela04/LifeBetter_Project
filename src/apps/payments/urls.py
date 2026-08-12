from django.urls import path
from django.views.generic import RedirectView
from .views import InitiatePaymentView, WebpayReturnView

app_name = 'payments'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False), name='payment_index'),
    path('pay/<int:bill_id>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('webpay-return/', WebpayReturnView.as_view(), name='webpay_return'),
]