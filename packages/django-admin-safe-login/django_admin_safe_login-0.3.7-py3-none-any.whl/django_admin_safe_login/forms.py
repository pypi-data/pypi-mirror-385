from django.contrib.admin.forms import AdminAuthenticationForm
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField
from django_secure_password_input.fields import DjangoSecurePasswordInput
from django.conf import settings

class AdminSafeAuthenticationForm(AdminAuthenticationForm):
    password = DjangoSecurePasswordInput(label=_("Password"))
    if getattr(settings, "DJANGO_ADMIN_SAFE_LOGIN_ENABLE_CAPTCHA", True):
        captcha = CaptchaField(label=_("Captcha"))
