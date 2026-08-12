# src/apps/condo/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.users.models import User
from apps.condo.models import Condominium, Department
from apps.expenses.models import CommonExpense
from apps.expenses.services import ExpenseCalculatorService
from apps.espacioscomunes.models import CommonArea


class Command(BaseCommand):
    help = "Puebla la base de datos con información de prueba para probar el MVP de LifeBetter"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Limpiando datos antiguos..."))
        
        # Eliminar condominios (por cascada elimina departamentos, boletas y reservas)
        Condominium.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Creando usuarios por Rol..."))
        
        # 1. Usuarios
        admin_user = User.objects.create_user(
            username="admin_comunidad",
            email="admin@lifebetter.cl",
            password="password123",
            role=User.Role.ADMIN,
            first_name="Carlos",
            last_name="Administrador"
        )
        
        conserje_user = User.objects.create_user(
            username="conserje_nocturno",
            email="conserje@lifebetter.cl",
            password="password123",
            role=User.Role.CONSERJE,
            first_name="Juan",
            last_name="Pérez"
        )

        residente_user = User.objects.create_user(
            username="residente_depto101",
            email="residente@lifebetter.cl",
            password="password123",
            role=User.Role.RESIDENTE,
            first_name="María",
            last_name="González"
        )

        # 2. Condominio
        self.stdout.write(self.style.SUCCESS("Creando Condominio y Departamentos..."))
        condo = Condominium.objects.create(
            name="Edificio Parque Central",
            rut="77.123.456-7",
            address="Av. Providencia 1234, Santiago"
        )

        # 3. Departamentos y Alícuotas (Sumatoria 1.00 = 100%)
        dept101 = Department.objects.create(
            condominium=condo,
            number="101",
            floor=1,
            resident=residente_user,
            share_percentage=Decimal('0.250000') # 25%
        )
        Department.objects.create(
            condominium=condo,
            number="102",
            floor=1,
            share_percentage=Decimal('0.250000') # 25%
        )
        Department.objects.create(
            condominium=condo,
            number="201",
            floor=2,
            share_percentage=Decimal('0.250000') # 25%
        )
        Department.objects.create(
            condominium=condo,
            number="202",
            floor=2,
            share_percentage=Decimal('0.250000') # 25%
        )

        # 4. Gasto Común y Generación de Boletas
        self.stdout.write(self.style.SUCCESS("Generando Gasto Común y Boletas..."))
        expense = CommonExpense.objects.create(
            condominium=condo,
            title="Gastos Comunes Agosto 2026",
            description="Luz comunitaria, Mantención de ascensores y Conserjería",
            period=timezone.now().date().replace(day=1),
            total_amount=Decimal('400000.00') # $400.000 total
        )

        due_date = timezone.now().date() + timedelta(days=15)
        count = ExpenseCalculatorService.generate_bills_for_expense(expense, due_date)

        # 5. Espacios Comunes
        self.stdout.write(self.style.SUCCESS("Creando Espacios Comunes..."))
        CommonArea.objects.create(
            condominium=condo,
            name="Quincho Panorámico Azotea",
            description="Equipado con parrilla a carbón, refrigerador y mesas para 20 personas.",
            capacity=20,
            fee=Decimal('15000.00')
        )
        CommonArea.objects.create(
            condominium=condo,
            name="Salón de Eventos / Multiuso",
            description="Sillas, mesas, equipo de sonido y cocina básica.",
            capacity=50,
            fee=Decimal('30000.00')
        )

        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("¡Base de datos poblada exitosamente!"))
        self.stdout.write(self.style.SUCCESS(f"Se crearon {count} boletas de $100.000 cada una (25% alícuota)."))
        self.stdout.write(self.style.SUCCESS("Credenciales de prueba para Residente:"))
        self.stdout.write(self.style.SUCCESS("   Email: residente@lifebetter.cl"))
        self.stdout.write(self.style.SUCCESS("   Clave: password123"))
        self.stdout.write(self.style.SUCCESS("=" * 50))