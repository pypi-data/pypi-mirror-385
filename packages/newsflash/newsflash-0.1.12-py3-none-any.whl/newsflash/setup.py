import os
from django.core.management import execute_from_command_line


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsflash.web.settings")
    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(["manage.py", "createcachetable"])
    execute_from_command_line(["manage.py", "collectstatic"])
