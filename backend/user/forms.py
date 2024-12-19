from django.contrib.auth.forms import UserChangeForm

from user.models import User


class UserChangeForm(UserChangeForm):
    """Форма для админской модели User"""

    class Meta(UserChangeForm.Meta):
        model = User
