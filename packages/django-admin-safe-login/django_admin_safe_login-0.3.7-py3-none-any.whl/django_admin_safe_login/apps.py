from django.apps import AppConfig


class DjangoAdminSafeLoginConfig(AppConfig):
    name = 'django_admin_safe_login'

    def ready(self):
        self.replace_admin_login_form()

    def replace_admin_login_form(self):
        from django.contrib import admin
        from django.conf import settings
        from .forms import AdminSafeAuthenticationForm

        django_admin_safe_login_enable_captcha = getattr(settings, "DJANGO_ADMIN_SAFE_LOGIN_ENABLE_CAPTCHA", True)
        django_admin_safe_login_template = getattr(settings, "DJANGO_ADMIN_SAFE_LOGIN_TEMPLATE", None)
        if django_admin_safe_login_enable_captcha is True or django_admin_safe_login_enable_captcha is None:
            admin.site.login_form = AdminSafeAuthenticationForm
            if django_admin_safe_login_template:
                admin.site.login_template = django_admin_safe_login_template
