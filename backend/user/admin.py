from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user.forms import UserChangeForm
from user.models import Follow, User

admin.site.empty_value_display = "-пусто-"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админская конфигурация для управления Пользователями."""

    form = UserChangeForm
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-зона подписок."""

    list_display = ('pk', 'subscriber', 'author')
    list_editable = ('subscriber', 'author')
    search_fields = ('subscriber__username', 'subscriber__email')
    list_filter = ('subscriber',)


admin.site.site_title = 'Администрирование Foodgram'
admin.site.site_header = 'Администрирование Foodgram'
