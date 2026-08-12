# src/core/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from apps.users.models import User
from apps.expenses.models import ExpenseBill, CommonExpense
from apps.espacioscomunes.models import Reservation  # Nota: usamos la app espacioscomunes


class LandingPageView(TemplateView):
    """Página pública de bienvenida."""
    template_name = 'landing.html'


class UserLoginView(LoginView):
    """Vista de inicio de sesión."""
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class UserLogoutView(LogoutView):
    """Vista de cierre de sesión."""
    next_page = reverse_lazy('landing')


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Controlador del Dashboard. Carga la plantilla según las subcarpetas organizadas por rol.
    """
    def get_template_names(self):
        user = self.request.user
        if user.role == User.Role.CONSERJE:
            return ['rol_conserje/dashboard_conserje.html']
        elif user.role == User.Role.ADMIN:
            return ['rol_admin/dashboard_admin.html']
        return ['rol_residente/dashboard_residente.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == User.Role.RESIDENTE:
            base_bills = ExpenseBill.objects.filter(
                department__resident=user
            ).select_related('department', 'common_expense').order_by('-due_date')
            
            context['pending_bills'] = base_bills.filter(status=ExpenseBill.Status.PENDING)
            context['recent_bills'] = base_bills[:5]
            context['recent_reservations'] = Reservation.objects.filter(
                user=user,
                status=Reservation.Status.CONFIRMED
            ).select_related('common_area').order_by('-start_time')[:5]

        elif user.role == User.Role.CONSERJE:
            context['today_reservations'] = Reservation.objects.filter(
                status=Reservation.Status.CONFIRMED
            ).select_related('common_area', 'department', 'user').order_by('start_time')[:10]

        elif user.role == User.Role.ADMIN:
            context['latest_expenses'] = CommonExpense.objects.select_related('condominium').order_by('-period')[:5]
            context['total_bills_pending'] = ExpenseBill.objects.filter(status=ExpenseBill.Status.PENDING).count()

        return context