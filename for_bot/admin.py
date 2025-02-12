from django.contrib import admin
from .models import TelegramUser, TelegramMessageLog,Domains

admin.site.register(TelegramUser)
admin.site.register(TelegramMessageLog)
@admin.register(Domains)
class DomainAdmin(admin.ModelAdmin):
    pass