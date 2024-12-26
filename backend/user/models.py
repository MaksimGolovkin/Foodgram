from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constant import (MAX_LEN_EMAIL, MAX_LEN_USERNAME_PASSWORD,
                          WRONGUSERNAME)
from user.validators import user_name_validator


class User(AbstractUser):
    """Кастомная модель пользователя.Регистрация с помощью email."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    username = models.CharField(
        "Имя пользователя",
        max_length=MAX_LEN_USERNAME_PASSWORD,
        unique=True,
        validators=[user_name_validator]
    )
    first_name = models.CharField(
        max_length=MAX_LEN_USERNAME_PASSWORD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LEN_USERNAME_PASSWORD,
        verbose_name='Имя'
    )
    email = models.EmailField(
        max_length=MAX_LEN_EMAIL,
        verbose_name='Электронная почта',
        unique=True
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )
    password = models.CharField(
        max_length=MAX_LEN_USERNAME_PASSWORD,
        verbose_name='Пароль'
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username=WRONGUSERNAME),
                name='username_not_me'
            )
        ]

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Модель подписчиков."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь',
        help_text='Текущий пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Подписка',
        help_text='Подписаться на автора рецепта(ов)'
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                name='unique_subscribed',
                fields=('subscriber', 'author'),
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='no_self_following'
            )
        ]

    def __str__(self):
        return f'{self.author} подписан на: {self.subscriber}'
