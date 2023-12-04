# Generated by Django 4.2.7 on 2023-12-04 04:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_email_verified",
            field=models.BooleanField(default=False, verbose_name="이메일 검증 여부"),
        ),
        migrations.AddField(
            model_name="user",
            name="point",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=255, unique=True, verbose_name="이메일"),
        ),
        migrations.CreateModel(
            name="VerificationCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="인증 코드 생성시간"),
                ),
                ("code", models.CharField(max_length=6, verbose_name="숫자 인증 코드")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="codes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="이메일 전송된 인증 코드",
                    ),
                ),
            ],
        ),
    ]