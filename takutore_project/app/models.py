from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
# ユーザー情報
class User(AbstractUser):
    first_name = None
    last_name = None
    date_joined = None
    groups = None
    user_permissions = None

    username = models.CharField(max_length=100, unique=True, verbose_name="ユーザー名")
    email = models.EmailField(max_length=255, unique=True, verbose_name="メールアドレス")
    height = models.FloatField(verbose_name="身長", null=True, blank=False)
    weight = models.FloatField(verbose_name="体重", null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = 'users'
