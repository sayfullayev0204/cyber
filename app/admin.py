from django.contrib import admin
from .models import (
    Channel,
    Group,
    MessageLog,
    ScheduledMessages,
    User,
    WeekDays,
    GroupCategory,
    BotToken,
)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ["name", "channel_id"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "group_id"]


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ["unique_id", "message_id", "channel", "group", "sent_at"]


@admin.register(ScheduledMessages)
class ScheduledMessagesAdmin(admin.ModelAdmin):
    list_display = ["id", "schedule_type"]
    filter_horizontal = ["weekly_days", "groups"]


admin.site.register(WeekDays)
admin.site.register(User)
admin.site.register(GroupCategory)
