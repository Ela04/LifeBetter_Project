from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema LifeBetter.
    Soporta Roles (RBAC) y extiende los campos estándar de Django.
    """
    @property
    def is_admin_or_staff(self):
        """Devuelve True si el usuario tiene rol ADMIN o permisos de staff en Django."""
        return self.role == self.Role.ADMIN or self.is_staff or self.is_superuser

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CONSERJE = 'CONSERJE', 'Conserje'
        RESIDENTE = 'RESIDENTE', 'Residente'

    email = models.EmailField(
        unique=True, 
        verbose_name="Correo Electrónico",
        error_messages={'unique': 'Ya existe un usuario registrado con este correo.'}
    )
    role = models.CharField(
        max_length=15, 
        choices=Role.choices, 
        default=Role.RESIDENTE,
        verbose_name="Rol de Usuario"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Teléfono de Contacto"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

class ForumPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='forum_posts',
        verbose_name="Autor"
    )
    title = models.CharField(max_length=200, verbose_name="Título del Anuncio/Discusión")
    content = models.TextField(verbose_name="Contenido (Admite Emojis 😃)")
    image = models.ImageField(
        upload_to='forum_images/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif'])],
        verbose_name="Imagen Adjunta (Opcional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Publicación del Foro"
        verbose_name_plural = "Publicaciones del Foro"

    def __str__(self):
        return f"{self.title} - {self.author.get_full_name() or self.author.email}"


class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario de {self.author.email} en '{self.post.title}'"