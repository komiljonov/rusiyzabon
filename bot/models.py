from io import BytesIO

from django.db import models
from pandas import DataFrame, ExcelWriter
from telegram import Update

from enums import PostMediaTypeEnum

# Create your models here.


class User(models.Model):
    chat_id = models.BigIntegerField(primary_key=True, unique=True)

    fullname = models.CharField(max_length=512)
    username = models.CharField(max_length=255, null=True, blank=True)

    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    check_file = models.FileField(upload_to="checks/")

    is_registered = models.BooleanField(default=False)

    admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    registered_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get(cls, update: Update):
        return (
            (user := update.effective_user),
            (
                db := cls.objects.filter(
                    chat_id=user.id,
                ).first()
                if user
                else None
            ),
            (db.temp if db else None),
        )

    @property
    def temp(self):
        return UserTemp.objects.get_or_create(user=self)[0]

    @classmethod
    def xlsx(cls):
        df = DataFrame(
            cls.objects.all().values(
                "chat_id",
                "fullname",
                "username",
                "name",
                "number",
                "is_registered",
                "admin",
                "registered_at",
            )
        ).rename(
            columns={
                "chat_id": "TG ID",
                "fullname": "TG NAME",
                "username": "TG USERNAME",
                "name": "Register Name",
                "number": "Register Number",
                "is_registered": "Is register complete",
                "admin": "Is Admin",
                "registered_at": "Ro'yxatdan o'tgan vaqti",
            }
        )
        res = BytesIO()
        writer = ExcelWriter(res, datetime_format="hh:mm:ss")
        df.to_excel(writer, sheet_name="Users", index=False)
        writer.close()
        res.seek(0)
        return res


class UserTemp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    post_media_type = models.IntegerField(
        choices=[
            (PostMediaTypeEnum.PHOTO, "PHOTO"),
            (PostMediaTypeEnum.VIDEO, "VIDEO"),
            (PostMediaTypeEnum.DOCUMENT, "DOCUMENT"),
            (PostMediaTypeEnum.TEXT, "TEXT"),
            (PostMediaTypeEnum.AUDIO, "AUDIO"),
            (PostMediaTypeEnum.VIDEO_NOTE, "VIDEO_NOTE"),
        ],
        default=0,
    )

    post_media_id = models.TextField(null=True, blank=True)
    post_media_width = models.IntegerField(null=True, blank=True)
    post_media_height = models.IntegerField(null=True, blank=True)
    post_media_duration = models.IntegerField(null=True, blank=True)

    post_media_filename = models.CharField(max_length=255)

    post_text = models.TextField(null=True, blank=True)

    str1 = models.TextField(null=True, blank=True)
    str2 = models.TextField(null=True, blank=True)
    str3 = models.TextField(null=True, blank=True)
    str4 = models.TextField(null=True, blank=True)
    str5 = models.TextField(null=True, blank=True)
    str6 = models.TextField(null=True, blank=True)
    str7 = models.TextField(null=True, blank=True)

    int1 = models.IntegerField(null=True, blank=True)
    int2 = models.IntegerField(null=True, blank=True)
    int3 = models.IntegerField(null=True, blank=True)
    int4 = models.IntegerField(null=True, blank=True)
    int5 = models.IntegerField(null=True, blank=True)
