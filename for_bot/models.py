from django.db import models
from app.models import Group

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username or str(self.telegram_id)




class Domains(models.Model):
    domain_suffix = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.domain_suffix


class TelegramMessageLog(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # Guruh bilan bog‘lash
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=100, null=True, blank=True)
    message_id = models.BigIntegerField()
    text = models.TextField(null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.username} in {self.group.name}"
