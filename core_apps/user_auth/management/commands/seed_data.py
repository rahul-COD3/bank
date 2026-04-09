import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.db.models import Q


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


class Command(BaseCommand):
    help = "Seed baseline data (migrations, superuser, optional fixtures)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-migrate",
            action="store_true",
            help="Skip running migrations before seeding.",
        )
        parser.add_argument(
            "--fixture",
            action="append",
            default=[],
            help="Fixture name/path to load. Can be provided multiple times.",
        )

    def handle(self, *args, **options):
        seed = {
            "email": require_env("SEED_SUPERUSER_EMAIL"),
            "password": require_env("SEED_SUPERUSER_PASSWORD"),
            "first_name": require_env("SEED_SUPERUSER_FIRST_NAME"),
            "middle_name": os.getenv("SEED_SUPERUSER_MIDDLE_NAME", ""),
            "last_name": require_env("SEED_SUPERUSER_LAST_NAME"),
            "security_question": require_env("SEED_SUPERUSER_SECURITY_QUESTION"),
            "security_answer": require_env("SEED_SUPERUSER_SECURITY_ANSWER"),
            "id_no": require_env("SEED_SUPERUSER_ID_NO"),
            "role": require_env("SEED_SUPERUSER_ROLE"),
        }

        os.environ.update(
            {
                "DJANGO_SUPERUSER_EMAIL": seed["email"],
                "DJANGO_SUPERUSER_PASSWORD": seed["password"],
                "DJANGO_SUPERUSER_FIRST_NAME": seed["first_name"],
                "DJANGO_SUPERUSER_LAST_NAME": seed["last_name"],
                "DJANGO_SUPERUSER_SECURITY_QUESTION": seed["security_question"],
                "DJANGO_SUPERUSER_SECURITY_ANSWER": seed["security_answer"],
                "DJANGO_SUPERUSER_ID_NO": str(seed["id_no"]),
            }
        )

        if not options["no_migrate"]:
            call_command("migrate", interactive=False, verbosity=0)

        user_model = get_user_model()
        user = user_model.objects.filter(Q(email__iexact=seed["email"]) | Q(id_no=int(seed["id_no"]))).first()

        if user is None:
            call_command("createsuperuser", interactive=False, verbosity=0)
            user = user_model.objects.get(email__iexact=seed["email"])
            action = "Created"
        else:
            action = "Updated"

        user.email = seed["email"]
        user.first_name = seed["first_name"]
        user.middle_name = seed["middle_name"]
        user.last_name = seed["last_name"]
        user.security_question = seed["security_question"]
        user.security_answer = seed["security_answer"]
        user.id_no = int(seed["id_no"])
        user.role = seed["role"]
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(seed["password"])
        user.save()

        self.stdout.write(self.style.SUCCESS(f"{action} superuser: {seed['email']}"))

        for fixture in options["fixture"]:
            call_command("loaddata", fixture)
            self.stdout.write(self.style.SUCCESS(f"Loaded fixture: {fixture}"))
