# src/apps/expenses/views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.exceptions import PermissionDenied

from .models import ExpenseBill
from .pdf_service import PDFGeneratorService


class DownloadBillPDFView(LoginRequiredMixin, View):
    """
    Vista que genera y sirve la boleta en formato PDF para descarga directa.
    """
    def get(self, request, pk, *args, **kwargs):
        bill = get_object_or_404(ExpenseBill.objects.select_related('department', 'department__condominium', 'department__resident', 'common_expense'), pk=pk)
        user = request.user

        # Control de Permisos (RBAC):
        # Un residente solo puede descargar las boletas asociadas a su departamento.
        is_owner = bill.department.resident == user
        is_admin_or_staff = user.role == 'ADMIN' or user.is_staff or user.is_superuser

        if not (is_owner or is_admin_or_staff):
            raise PermissionDenied("No tienes permisos para acceder a esta boleta.")

        pdf_bytes = PDFGeneratorService.generate_expense_bill_pdf(bill)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"Boleta_Depto_{bill.department.number}_Periodo_{bill.common_expense.period.strftime('%Y_%m')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response