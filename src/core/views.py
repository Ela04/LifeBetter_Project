from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from apps.expenses.models import ExpenseBill
from apps.espacioscomunes.models import Reservation


class LandingPageView(TemplateView):
    template_name = 'landing.html'


class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('landing')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch de boletas optimizado
        base_bills = ExpenseBill.objects.filter(
            department__resident=user
        ).select_related('department', 'common_expense').order_by('-due_date')

        pending_bills = base_bills.filter(status=ExpenseBill.Status.PENDING)

        # Fetch de reservas
        reservations = Reservation.objects.filter(
            user=user,
            status=Reservation.Status.CONFIRMED
        ).select_related('common_area', 'department').order_by('-start_time')[:5]

        context['pending_bills'] = pending_bills
        context['recent_bills'] = base_bills[:5]
        context['recent_reservations'] = reservations
        return context