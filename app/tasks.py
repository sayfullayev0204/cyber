import asyncio

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from datetime import timedelta
from app.models import MessageLog, Channel, Group, ScheduledMessages, BotToken


def get_bot_token():
    bot_config = BotToken.objects.first()
    if bot_config:
        return bot_config.token
    raise ValueError("Bot token topilmadi! Iltimos, bazaga token qo'shing.")

bot = Bot(token=get_bot_token())


async def send_message(channel_id, message_id, group_id):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Kanalni ochish",
                url="https://t.me/cyber_102"
            )
        ]
    ])

    try:
        await bot.copy_message(
            chat_id=group_id,
            from_chat_id=channel_id,
            message_id=message_id,
            reply_markup=inline_kb
        )
        # Ma'lumotlarni bazaga yozish
        channel = await sync_to_async(Channel.objects.get)(channel_id=channel_id)
        group = await sync_to_async(Group.objects.get)(group_id=group_id)

        await sync_to_async(MessageLog.objects.create)(
            message_id=message_id,
            channel=channel,
            group=group
        )
    except Exception as e:
        print(f"Error sending message: {e}")


@shared_task
def send_message_task(channel_id, message_id, group_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message(channel_id, message_id, group_id))

@shared_task
def process_scheduled_messages():
    current_time = timezone.now() + timedelta(hours=5)  # Toshkent vaqti uchun
    scheduled_messages = ScheduledMessages.objects.filter(is_active=False)

    for schedule in scheduled_messages:
        if schedule.schedule_type == 'onetime':
            schedule.is_active = True
            schedule.save(update_fields=['is_active'])
            send_scheduled_message(schedule)

        elif schedule.schedule_type == 'daily':
            schedule_time = datetime.combine(current_time.date(), schedule.day_time)
            current_time_combined = datetime.combine(current_time.date(), current_time.time())

            if abs((schedule_time - current_time_combined).total_seconds()) <= 60:
                schedule.is_active = True
                schedule.save(update_fields=['is_active'])
                send_scheduled_message(schedule)

        elif schedule.schedule_type == 'repedly':
            today_weekday = current_time.strftime('%A')
            if schedule.weekly_days.filter(name=today_weekday).exists() and schedule.repetly_time == current_time.time():
                schedule.is_active = True
                schedule.save(update_fields=['is_active'])
                send_scheduled_message(schedule)

def send_scheduled_message(schedule):
    for group in schedule.groups.all():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_message(schedule.channel.channel_id, schedule.message_id, group.group_id))