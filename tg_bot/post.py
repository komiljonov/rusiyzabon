from io import BytesIO

from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    ExtBot,
    MessageHandler,
    filters,
)
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeImageSize, DocumentAttributeVideo

from bot.models import User
from constants import ADMIN_POST_CHECK, ADMIN_POST_MEDIA, BACK, EXCLUDE, MENU
from enums import PostMediaTypeEnum
from utils import ReplyKeyboardMarkup


class Post:
    bot: ExtBot

    def postHandlers(self):
        return ConversationHandler(
            [MessageHandler(filters.Text(["Post yuborish"]), self.send_post)],
            {
                ADMIN_POST_MEDIA: [
                    MessageHandler(
                        filters.VIDEO
                        | filters.PHOTO
                        | filters.Document.ALL
                        | filters.VIDEO_NOTE
                        | filters.TEXT & EXCLUDE,
                        self.send_post_media,
                    ),
                    MessageHandler(filters.Text([BACK]), self.start),
                ],
                ADMIN_POST_CHECK: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.admin_post_check),
                    MessageHandler(filters.Text([BACK]), self.send_post),
                ],
            },
            [],
            map_to_parent={MENU: MENU},
        )

    async def send_post(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        await tgUser.send_message(
            "Post uchun media yuboring.", reply_markup=ReplyKeyboardMarkup()
        )
        return ADMIN_POST_MEDIA

    async def send_post_media(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)
        media_type = (
            PostMediaTypeEnum.VIDEO
            if update.message.video
            else (
                PostMediaTypeEnum.VIDEO_NOTE
                if update.message.video_note
                else (
                    PostMediaTypeEnum.PHOTO
                    if update.message.photo
                    else (
                        PostMediaTypeEnum.DOCUMENT
                        if update.message.document
                        else PostMediaTypeEnum.TEXT
                    )
                )
            )
        )

        temp.int1 = media_type
        temp.str1 = (
            update.message.text_html_urled
            if media_type == PostMediaTypeEnum.TEXT
            else update.message.caption_html_urled
        )

        f = (
            update.message.effective_attachment[-1]
            if update.message.photo
            else update.message.effective_attachment
        )
        if media_type == PostMediaTypeEnum.VIDEO:
            temp.int2 = f.duration
            temp.int3 = f.width
            temp.int4 = f.height

        if media_type == PostMediaTypeEnum.VIDEO_NOTE:
            temp.int2 = f.duration

        if media_type == PostMediaTypeEnum.PHOTO:
            temp.int3 = f.width
            temp.int4 = f.height

        try:
            fname = f.file_name
            temp.str5 = fname
        except Exception:
            temp.str5 = "photo.png" if update.message.photo else "video.mp4"

        temp.str2 = f.file_id if f else ""
        temp.save()
        await tgUser.send_message("Iltimos postni tekshiring.")
        await self.send(update, context)
        return ADMIN_POST_CHECK

    async def send(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        keyboard = ReplyKeyboardMarkup([["Yuborish", "Bekor qilish"]])

        if temp.int1 == PostMediaTypeEnum.TEXT:
            await tgUser.send_message(
                temp.str1,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        elif temp.int1 == PostMediaTypeEnum.VIDEO:
            await tgUser.send_video(
                temp.str2,
                caption=temp.str1,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        elif temp.int1 == PostMediaTypeEnum.VIDEO_NOTE:
            await tgUser.send_video_note(
                temp.str2,
            )
            await tgUser.send_message(
                "Tasdiqlaysizmi?2",
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        elif temp.int1 == PostMediaTypeEnum.PHOTO:
            await tgUser.send_photo(
                temp.str2,
                caption=temp.str1,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        elif temp.int1 == PostMediaTypeEnum.DOCUMENT:
            await tgUser.send_document(
                temp.str2,
                caption=temp.str1,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

    async def admin_post_check(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        a = (
            (update.message.text == "Yuborish")
            if update.message.text in ["Yuborish", "Bekor qilish"]
            else None
        )
        print(a)

        if a is None:
            await tgUser.send_message(
                "Yuborilsinmi yoki bekor qilinsinmi?",
                reply_markup=ReplyKeyboardMarkup([["Yuborish", "Bekor qilish"]]),
            )
            return ADMIN_POST_CHECK

        await tgUser.send_message(
            "Habarlar yuborilmoqda.\n\nIltimos kuting biroz vaqt ketadi."
        )

        await self.send_post_to_users(update, context)

        return await self.start(update, context)

    async def send_post_to_users(self, update: Update, context: CallbackContext):
        tgUser, user, temp = User.get(update)

        client = TelegramClient(
            f"PostClient_{user.chat_id}.session",
            1576297,
            "4baa5091b96708ed0aebc626dc404ff9",
        )

        await client.start(bot_token=self.token)

        f = None

        if temp.int1 in [
            PostMediaTypeEnum.VIDEO,
            PostMediaTypeEnum.PHOTO,
            PostMediaTypeEnum.DOCUMENT,
            PostMediaTypeEnum.VIDEO_NOTE,
        ]:
            tf = await self.bot.get_file(temp.str2)

            c = BytesIO()
            await tf.download_to_memory(c)
            c.seek(0)

            f = await client.upload_file(
                c,
                file_name=temp.str5,
            )

        users = User.objects.all()
        sent = 0
        fail = 0

        p_m = await tgUser.send_message(
            "Post yuborilmoqda.\n\n"
            f"Yuborildi: {sent}\n"
            f"Yuborib bo'lmadi: {fail}\n"
            f"Process: 0%"
        )

        for i in range(len(users)):
            u = users[i]
            if temp.int1 == PostMediaTypeEnum.TEXT:
                try:
                    await client.send_message(u.chat_id, temp.str1, parse_mode="html")
                    sent += 1
                except Exception as e:
                    print(e)
                    fail += 1
            elif temp.int1 == PostMediaTypeEnum.VIDEO:
                try:
                    await client.send_file(
                        u.chat_id,
                        f,
                        caption=temp.str1,
                        file_size=tf.file_size,
                        parse_mode="html",
                        attributes=[
                            DocumentAttributeVideo(temp.int2, temp.int3, temp.int4)
                        ],
                    )
                    sent += 1
                except Exception as e:
                    print(e)
                    fail += 1
            elif temp.int1 == PostMediaTypeEnum.VIDEO_NOTE:
                try:
                    await client.send_file(
                        u.chat_id,
                        f,
                        video_note=True,
                        file_size=tf.file_size,
                    )
                    sent += 1
                except Exception as e:
                    print(e)
                    fail += 1
            elif temp.int1 == PostMediaTypeEnum.PHOTO:
                try:
                    await client.send_file(
                        u.chat_id,
                        f,
                        caption=temp.str1,
                        file_size=tf.file_size,
                        parse_mode="html",
                        attributes=[DocumentAttributeImageSize(temp.int3, temp.int4)],
                    )
                    sent += 1
                except Exception as e:
                    print(e)
                    fail += 1
            elif temp.int1 == PostMediaTypeEnum.DOCUMENT:
                try:
                    await client.send_file(
                        u.chat_id,
                        f,
                        file_size=tf.file_size,
                        caption=temp.str1,
                        parse_mode="html",
                    )
                    sent += 1
                except Exception as e:
                    print(e)
                    fail += 1
            if i % 100 == 0:
                # await tgUser.send_message(i)
                await p_m.edit_text(
                    "Post yuborilmoqda.\n\n"
                    f"Yuborildi: {sent}\n"
                    f"Yuborib bo'lmadi: {fail}\n"
                    f"Process: {((sent + fail) / users.count()) * 100 }%"
                )
        await client.log_out()

        await tgUser.send_message("Habarlar yuborildi.")
