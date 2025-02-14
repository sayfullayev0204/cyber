import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
import pytz
from django.utils.timezone import now


class GroupCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class BotToken(models.Model):
    token = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.token


class Channel(models.Model):
    channel_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Group(models.Model):
    group_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(GroupCategory, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)  # Bot admin yoki yo‘qligini tekshirish uchun

    def __str__(self):
        return self.name




class MessageLog(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    message_id = models.CharField(max_length=50)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Message: {self.message_id} to Group: {self.group.name}"


class WeekDays(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class ScheduledMessages(models.Model):
    SCHEDULE_TYPES = [
        ("onetime", "One Time"),
        ("daily", "Daily"),
        ("repedly", "Repedly"),
    ]
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message_id = models.IntegerField()
    schedule_type = models.CharField(max_length=10, choices=SCHEDULE_TYPES)
    # kunlik
    day_time = models.TimeField(null=True, blank=True)
    day_date = models.DateField(null=True, blank=True)
    # takroriy
    start_day = models.DateField(null=True, blank=True)
    end_day = models.DateField(null=True, blank=True)
    repetly_time = models.TimeField(null=True, blank=True)
    weekly_days = models.ManyToManyField(WeekDays, blank=True)

    groups = models.ManyToManyField(Group)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f"Message ID: {self.title}, Schedule Type: {self.schedule_type}"


class User(AbstractUser):
    ROLE_CHOICES = [
        ("superuser", "superuser"),
        ("monitoring", "monitoring"),
        ("postmaker", "postmaker"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Adminlar"
        verbose_name_plural = "Adminlar"
