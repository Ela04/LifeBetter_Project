from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ForumPost, ForumComment


class ForumCommentInline(admin.TabularInline):
    """
    Permite visualizar y crear comentarios directamente 
    dentro de la vista de edición de una publicación.
    """
    model = ForumComment
    extra = 1
    fields = ['author', 'content', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para las Publicaciones del Foro.
    """
    list_display = ['title', 'author', 'created_at', 'comments_count', 'has_image']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content', 'author__email', 'author__first_name']
    ordering = ['-created_at']
    raw_id_fields = ['author']  # Mejora el rendimiento en bases de datos con muchos usuarios
    inlines = [ForumCommentInline]

    @admin.display(description='Comentarios')
    def comments_count(self, obj):
        return obj.comments.count()

    @admin.display(description='Imagen', boolean=True)
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    """
    Gestión independiente de comentarios desde el Admin.
    """
    list_display = ['post', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__email', 'post__title']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'role', 'phone_number', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = UserAdmin.fieldsets + (
        ('Atributos de Dominio (LifeBetter RBAC)', {'fields': ('role', 'phone_number')}),
    )