from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Crea los grupos de usuarios iniciales para el sistema de stock"

    def handle(self, *args, **kwargs):
        roles = ['Ventas', 'Administrativo', 'Camiones']
        for rol in roles:
            group, created = Group.objects.get_or_create(name=rol)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Grupo '{rol}' creado"))
            else:
                self.stdout.write(f"Grupo '{rol}' ya existía")