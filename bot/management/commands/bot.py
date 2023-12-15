import os
from typing import Any
from django.core.management.base import BaseCommand












class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        TOKEN = os.getenv("TOKEN")

        
