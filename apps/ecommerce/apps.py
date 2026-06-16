"""
Apps configuration for ecommerce.
"""
from django.apps import AppConfig


class ECommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ecommerce'
    verbose_name = 'ระบบขายหน้าเว็บ'
