import os
from typing import Any
from django.core.management.base import BaseCommand
from tg_bot import Bot











class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        TOKEN = os.getenv("TOKEN")
        bot = Bot(TOKEN)

        bot.app.run_polling()

