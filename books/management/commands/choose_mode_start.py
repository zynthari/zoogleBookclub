from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Запуск Django с выбором embedding модели. Идея благая, но не реализованная"

    def handle(self, *args, **options):
        self.stdout.write("Выбери модель:")
        self.stdout.write("1. локальная")
        self.stdout.write("2. API")

        choice = input("Твой выбор: ")

        if choice not in ("1", "2"):
            self.stderr.write("Неверный выбор")
            return

        call_command("runserver", "0.0.0.0:8000", use_reloader=False)