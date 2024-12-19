from django.core.validators import RegexValidator

from api.constant import REGEXUSERNAME

# Проверка на корректность ввода Username.
user_name_validator = RegexValidator(
    regex=REGEXUSERNAME,
    message='Username contains invalid characters'
)
