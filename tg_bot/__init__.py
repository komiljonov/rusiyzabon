from io import BytesIO
from telegram import (
    KeyboardButton,
    ReplyKeyboardRemove,
    Update,
)


from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ExtBot,
)

from bot.models import User
from constants import CHECK, EXCLUDE, MENU, NAME, NUMBER, PASSWORD
from tg_bot.post import Post
from utils import ReplyKeyboardMarkup
from django.core.files.base import File
from django.utils.timezone import now


class Bot(Post):
    bot: ExtBot

    def __init__(self, token: str):
        self.token = token

        self.app = (
            ApplicationBuilder().token(self.token).concurrent_updates(128).build()
        )
        self.bot = self.app.bot

        self.app.add_handler(
            ConversationHandler(
                [CommandHandler("start", self.start)],
                {
                    NAME: [MessageHandler(filters.TEXT & EXCLUDE, self.name)],
                    NUMBER: [
                        MessageHandler(
                            filters.Regex(
                                r"(?:(\+)?[9]{2}[8][0-9]{2}[0-9]{3}[0-9]{2}[0-9]{2})|([\d]{2}[0-9]{3}[0-9]{2}[0-9]{2})"
                            )
                            | filters.CONTACT,
                            self.number,
                        )
                    ],
                    CHECK: [MessageHandler(filters.PHOTO, self.check)],
                    MENU: [
                        MessageHandler(filters.Text(["Leadlar"]), self.leads),
                        self.postHandlers(),
                    ],
                },
                [CommandHandler("start", self.start)],
            )
        )

    async def start(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        if not user:
            user = User.objects.create(
                chat_id=tgUser.id,
                fullname=tgUser.full_name,
                username=tgUser.username,
            )
            temp = user.temp

        if context.args:
            if context.args[0] == PASSWORD:
                user.admin = True
                user.save()

        if user.admin:
            await tgUser.send_message(
                "Menu.",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [
                            "Leadlar",
                            "Post yuborish",
                        ]
                    ],
                    False,
                ),
            )
            return MENU

        if not user.is_registered:
            await tgUser.send_message(
                "<b>🖊 Iltimos ismingizni yuboring!</b>", reply_markup=ReplyKeyboardRemove(),parse_mode="HTML"
            )
            return NAME

        await tgUser.send_message(
            "<b>❌ Qaytadan ro'yxatdan o'tib bo'lmaydi</b>\n\n"
            "🧑🏻‍💻 Biz bilan bog'lanish uchun @bic_manager",parse_mode="HTML")
        return -1

    async def name(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        user.name = update.message.text
        user.save()

        await tgUser.send_message(
            "<b>📞 Sizga qo'ng'iroq qilishimiz uchun raqamingizni qoldiring!\n\n"
                "<i>(Masalan: +998997774455)</i></b>",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Raqamni yuborish", request_contact=True)]]
            ),
            parse_mode="HTML"
        )
        return NUMBER

    async def number(self, update: Update, context: CallbackContext):
        tgUser, user, tmp = User.get(update)

        number = (
            update.message.contact.phone_number
            if update.message.contact
            else update.message.text
        )

        user.number = number
        user.save()

        # await tgUser.send_video("video.mp4",caption="Tabriklaymiz siz muvaffaqiyatli ro'yxatdan o'tdingiz.",reply_markup=ReplyKeyboardRemove())
        # await tgUser.send_video_note("DQACAgQAAxkBAAIBRGVm8xnvgYhkAQ9uvFx7DU78AAGhMAACBBMAAnWUMFN95f-r2FBx9DME",44,384)
        # await tgUser.send_message("https://youtu.be/s0jYB3v3k0M")

        await tgUser.send_message(
            "<b>📩 To'lovni tasdiqlovchi chekni yuboring!</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )

        return CHECK

    async def check(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        file = await update.message.effective_attachment[-1].get_file()

        fileformat = file.file_path.split(".")[-1]

        c = BytesIO()
        file.download_to_memory(c)
        c.seek(0)

        f = File(c, name=f"check_{tgUser.id}.{fileformat}")

        user.check_file = f
        user.is_registered = True
        user.registered_at = now()
        user.save()

        await self.bot.send_photo(
            -1002028915399,
            file.file_id,
            f"Ismi: {user.name}\n"
            f"Raqami: {user.number}\n"
            f"Vaqt: {user.registered_at.strftime('%d/%m/%Y, %H:%M:%S')}",
        )

        await tgUser.send_message(
            "<b>Tabriklayman 🥳</b>\n\n"
            "Siz <b>`Rus tilida 2024-yilda gapiring!`</b> nomli kursimga muavvafaqiyatli ro'yxatdan o'tdingiz. Tez orada menejerlar sizni chekingizni tekshirib, aloqaga chiqadi 🧑🏻‍💻.\n\n"
            "<i>Savollaringiz bo'lsa yozishingiz mumkin 👇😊</i>\n\n"
            "🧑🏻‍💻 Biz bilan bog'lanish uchun @bic_manager",parse_mode="HTML")

        return -1

    async def leads(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        xlsx = User.xlsx()

        await tgUser.send_document(
            xlsx,
            f"Foydalanuvchilar: {User.objects.count()}\n"
            f"Ro'yxatdan o'tgan: {User.objects.filter(is_registered=True).count()}",
            filename="users.xlsx",
        )
        return await self.start(update, context)
