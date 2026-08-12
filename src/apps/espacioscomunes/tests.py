import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta

from apps.users.models import User
from apps.condo.models import Condominium, Department
from apps.espacioscomunes.models import CommonArea, Reservation


@pytest.mark.django_db
def test_create_reservation_success():
    """
    Verifica que un residente pueda reservar un espacio común de forma exitosa.
    """
    # 1. Setup
    user = User.objects.create_user(
        username="residente_test",
        email="residente@test.cl",
        password="password123",
        role=User.Role.RESIDENTE
    )
    condo = Condominium.objects.create(
        name="Edificio Test", rut="22.222.222-2", address="Av. Test 456"
    )
    dept = Department.objects.create(
        condominium=condo, number="202", resident=user, share_percentage=Decimal('0.500000')
    )
    area = CommonArea.objects.create(
        condominium=condo, name="Quincho", capacity=15, fee=Decimal('10000.00')
    )

    start = timezone.now() + timedelta(days=1, hours=14)
    end = start + timedelta(hours=4)

    # 2. Ejecución
    reservation = Reservation.objects.create(
        common_area=area,
        department=dept,
        user=user,
        start_time=start,
        end_time=end,
        status=Reservation.Status.CONFIRMED
    )

    # 3. Assertions
    assert reservation.pk is not None
    assert reservation.status == Reservation.Status.CONFIRMED
    assert "Quincho" in str(reservation)


@pytest.mark.django_db
def test_prevent_overlapping_reservations():
    """
    Verifica que el sistema lance un ValidationError si se intenta reservar
    un espacio común en un rango de horario que ya está ocupado (traslape).
    """
    # 1. Setup inicial
    user1 = User.objects.create_user(username="res1", email="res1@test.cl", password="123", role=User.Role.RESIDENTE)
    user2 = User.objects.create_user(username="res2", email="res2@test.cl", password="123", role=User.Role.RESIDENTE)
    
    condo = Condominium.objects.create(name="Edificio Test 2", rut="33.333.333-3", address="Test 789")
    
    dept1 = Department.objects.create(condominium=condo, number="301", resident=user1, share_percentage=Decimal('0.50'))
    dept2 = Department.objects.create(condominium=condo, number="302", resident=user2, share_percentage=Decimal('0.50'))
    
    area = CommonArea.objects.create(condominium=condo, name="Salón de Eventos", capacity=40)

    base_time = timezone.now() + timedelta(days=2)
    start1 = base_time.replace(hour=15, minute=0, second=0, microsecond=0)
    end1 = start1 + timedelta(hours=5) # 15:00 a 20:00

    # Primera reserva exitosa
    Reservation.objects.create(
        common_area=area, department=dept1, user=user1, start_time=start1, end_time=end1
    )

    # 2. Intentar crear una reserva traslapada (ej: de 18:00 a 22:00)
    start_overlap = start1 + timedelta(hours=3)
    end_overlap = end1 + timedelta(hours=2)

    overlapping_reservation = Reservation(
        common_area=area,
        department=dept2,
        user=user2,
        start_time=start_overlap,
        end_time=end_overlap
    )

    # 3. Assertions: Validar que el método clean() bloquee el traslape
    with pytest.raises(ValidationError) as excinfo:
        overlapping_reservation.full_clean()
    
    assert "El espacio ya se encuentra reservado" in str(excinfo.value)