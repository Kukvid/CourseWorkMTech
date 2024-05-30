from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(upload_to="users_images", blank=True, null=True, verbose_name="Аватар")

    phone_number = models.CharField(max_length=10, blank=True, null=True)
    bonuses = models.DecimalField(verbose_name="Бонусы", default=50, max_digits=7, decimal_places=2)

    class Meta:
        db_table = "user"
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username
