from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

from .models import ForumPost, ForumComment
from apps.condo.models import Department

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'rol_residente/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['department'] = Department.objects.filter(resident=user).select_related('condominium').first()
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', getattr(user, 'phone', ''))
        user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('profile')


class ForumListView(LoginRequiredMixin, ListView):
    model = ForumPost
    template_name = 'rol_residente/forum_list.html'
    context_object_name = 'posts'
    paginate_by = 15

    def get_queryset(self):
        # Evitamos problema N+1 al cargar autores y comentarios en batch
        return ForumPost.objects.select_related('author').prefetch_related(
            'comments', 'comments__author'
        ).all()

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if title and content:
            ForumPost.objects.create(
                author=request.user,
                title=title,
                content=content,
                image=image
            )
            messages.success(request, '¡Publicación creada exitosamente! 🚀')
        else:
            messages.error(request, 'Por favor completa el título y el contenido.')

        return redirect('forum_list')

class ForumDetailView(LoginRequiredMixin, DetailView):
    model = ForumPost
    template_name = 'rol_residente/forum_detail.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        content = request.POST.get('content')
        if content:
            ForumComment.objects.create(post=post, author=request.user, content=content)
            messages.success(request, 'Comentario añadido.')
        return redirect('forum_detail', pk=post.pk)

class ForumPostDeleteView(LoginRequiredMixin, DeleteView):
    """
    Controlador para eliminar publicaciones del foro.
    Verifica que el usuario solicitante sea el autor o Administrador.
    """
    model = ForumPost
    success_url = reverse_lazy('forum_list')

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        user = self.request.user

        # Regla de Negocio: Solo autor o Administrador/Staff pueden eliminar
        is_author = post.author == user
        is_admin = user.role == 'ADMIN' or user.is_staff or user.is_superuser

        if not (is_author or is_admin):
            raise PermissionDenied("No tienes permisos para eliminar esta publicación.")
        
        return post

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Publicación eliminada correctamente.')
        return super().post(request, *args, **kwargs)