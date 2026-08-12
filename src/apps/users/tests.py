import pytest
from apps.users.models import User

@pytest.mark.django_db
def test_create_residente_user():
    """
    Verifica la creación correcta de un usuario con rol RESIDENTE.
    """
    user = User.objects.create_user(
        username="test_residente",
        email="test@lifebetter.cl",
        password="password123",
        role=User.Role.RESIDENTE
    )
    assert user.email == "test@lifebetter.cl"
    assert user.role == User.Role.RESIDENTE
    assert user.check_password("password123") is True


@pytest.mark.django_db
def test_create_user_with_roles():
    """
    Verifica la creación de usuarios con sus respectivos roles del enum Role.
    """
    admin_user = User.objects.create_user(
        username="admin_test",
        email="admin@test.cl",
        password="password123",
        role=User.Role.ADMIN
    )
    residente_user = User.objects.create_user(
        username="residente_test",
        email="residente@test.cl",
        password="password123",
        role=User.Role.RESIDENTE
    )

    assert admin_user.role == User.Role.ADMIN
    assert residente_user.role == User.Role.RESIDENTE
    assert admin_user.check_password("password123") is True


@pytest.mark.django_db
def test_user_is_admin_or_staff_property():
    """
    Prueba la propiedad de conveniencia is_admin_or_staff utilizada en la barra de navegación.
    """
    admin_user = User.objects.create_user(
        username="admin_role",
        email="admin_role@test.cl",
        password="123",
        role=User.Role.ADMIN
    )
    residente_user = User.objects.create_user(
        username="residente_role",
        email="residente_role@test.cl",
        password="123",
        role=User.Role.RESIDENTE
    )

    # Verificación de la propiedad de permisos helper
    assert admin_user.is_admin_or_staff is True
    assert residente_user.is_admin_or_staff is False