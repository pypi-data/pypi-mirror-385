import os
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key

class Command(BaseCommand):
    help = "Генерирует SECRET_KEY и сохраняет в .env в указанной папке"

    def add_arguments(self, parser):
        parser.add_argument("dir", type=str, help="Папка для .env файла")

    def handle(self, *args, **options):
        directory = options["dir"]
        env_path = os.path.join(directory, ".env")

        key = get_random_secret_key()

        # Если .env нет — создать
        if not os.path.exists(env_path):
            with open(env_path, "w") as f:
                f.write(f"SECRET_KEY={key}\n")
            self.stdout.write(self.style.SUCCESS(f".env создан и ключ добавлен"))
            return

        # Если .env есть — заменить или добавить SECRET_KEY
        with open(env_path, "r") as f:
            lines = f.readlines()

        updated = False
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith("SECRET_KEY="):
                    f.write(f"SECRET_KEY={key}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"\nSECRET_KEY={key}\n")

        self.stdout.write(self.style.SUCCESS("SECRET_KEY обновлён"))
