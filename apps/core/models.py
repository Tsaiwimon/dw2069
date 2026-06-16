"""
Base models for Tsaiwimon.
"""
from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """
    Base model with timestamp fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='เวลาสร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='เวลาแก้ไข')

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """
    Base model with soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False, verbose_name='ถูกลบ')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='เวลาลบ')

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Base model with active/inactive status.
    """
    is_active = models.BooleanField(default=True, verbose_name='ใช้งาน')

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, ActiveModel):
    """
    Combined base model with timestamp and active fields.
    """
    class Meta:
        abstract = True
        ordering = ['-created_at']


# User Profile Extension
class UserProfile(BaseModel):
    """
    Extended user profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name='โทรศัพท์')
    address = models.TextField(blank=True, verbose_name='ที่อยู่')
    postal_code = models.CharField(max_length=10, blank=True, verbose_name='รหัสไปรษณีย์')
    city = models.CharField(max_length=100, blank=True, verbose_name='เมือง')
    province = models.CharField(max_length=100, blank=True, verbose_name='จังหวัด')
    country = models.CharField(max_length=100, default='Thailand', verbose_name='ประเทศ')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='รูปโปรไฟล์')

    class Meta:
        verbose_name = 'โปรไฟล์ผู้ใช้'
        verbose_name_plural = 'โปรไฟล์ผู้ใช้'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} Profile'
