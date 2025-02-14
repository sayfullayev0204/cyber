import asyncio
from datetime import datetime
from datetime import timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from celery import shared_task
from django.utils import timezone

from app.models import MessageLog, Channel, Group, ScheduledMessages, BotToken


def get_bot_token():
    bot_config = BotToken.objects.first()
    if bot_config:
        return bot_config.token
    raise ValueError("Bot token topilmadi! Iltimos, bazaga token qo'shing.")


bot = Bot(token=get_bot_token())


async def send_message(channel_id, message_id, group_id):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Kanalni ochish", url="https://t.me/cyber_102")]
        ]
    )

    try:
        await bot.copy_message(
            chat_id=group_id,
            from_chat_id=channel_id,
            message_id=message_id,
            reply_markup=inline_kb,
        )
        # Ma'lumotlarni bazaga yozish
        channel = await sync_to_async(Channel.objects.get)(channel_id=channel_id)
        group = await sync_to_async(Group.objects.get)(group_id=group_id)

        await sync_to_async(MessageLog.objects.create)(
            message_id=message_id, channel=channel, group=group
        )
    except Exception as e:
        print(f"Error sending message: {e}")


@shared_task
def send_message_task(channel_id, message_id, group_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message(channel_id, message_id, group_id))


@shared_task
def process_scheduled_messages():
    # Toshkent vaqti uchun lokal vaqtni hisobga olish (agar server UTC bo'lsa)
    current_time = timezone.now() + timedelta(hours=5)

    # One-time xabarlarni faqat bir marta yuborish uchun
    one_time_messages = ScheduledMessages.objects.filter(
        schedule_type="onetime", is_active=False
    )
    # Daily va repedly xabarlarni filtrlamaymiz, chunki ular har 1 daqiqada tekshiriladi
    other_messages = ScheduledMessages.objects.exclude(schedule_type="onetime")

    # One-time xabarlar
    for schedule in one_time_messages:
        schedule.is_active = True  # Xabar yuborilgandan keyin flag-ni yangilaymiz
        schedule.save(update_fields=["is_active"])
        send_scheduled_message(schedule)

    # Daily va repedly xabarlar uchun:
    for schedule in other_messages:
        if schedule.schedule_type == "daily":
            # Bugungi belgilangan vaqt (kun + vaqt)
            schedule_time = datetime.combine(current_time.date(), schedule.day_time)
            current_time_combined = datetime.combine(
                current_time.date(), current_time.time()
            )

            # Agar belgilangan vaqt va joriy vaqt orasidagi farq 90 soniyadan kam bo'lsa, yuborish
            if abs((schedule_time - current_time_combined).total_seconds()) <= 90:
                send_scheduled_message(schedule)

        elif schedule.schedule_type == "repedly":
            # Bugungi hafta kuni (masalan, "Monday", "Tuesday", ...)
            today_weekday = current_time.strftime("%A")
            if today_weekday == "Monday":
                today_weekday = "Dushanba"
            elif today_weekday == "Tuesday":
                today_weekday = "Seshanba"
            elif today_weekday == "Wednesday":
                today_weekday = "Chorshanba"
            elif today_weekday == "Thursday":
                today_weekday = "Payshanba"
            elif today_weekday == "Friday":
                today_weekday = "Juma"
            elif today_weekday == "Saturday":
                today_weekday = "Shanba"
            elif today_weekday == "Sunday":
                today_weekday = "Yakshanba"
            # Bugungi sana
            today_date = current_time.date()
            print("====================================")
            print(today_weekday)
            print("====================================")
            # Agar belgilangan haftaning kunlari orasida bo'lsa
            if schedule.weekly_days.filter(name=today_weekday).exists():
                print("====================================")
                print("Kunlar mos keladi")
                print("====================================")
                scheduled_dt = datetime.combine(
                    current_time.date(), schedule.repetly_time
                )
                current_dt = datetime.combine(current_time.date(), current_time.time())
                # + / - 90 soniyalik oynani hisobga olamiz
                if abs((scheduled_dt - current_dt).total_seconds()) <= 65:
                    send_scheduled_message(schedule)
            elif schedule.start_day and schedule.end_day and schedule.start_day <= today_date <= schedule.end_day:
                scheduled_dt = datetime.combine(current_time.date(), schedule.repetly_time)
                current_dt = datetime.combine(current_time.date(), current_time.time())
                if abs((scheduled_dt - current_dt).total_seconds()) <= 65:
                    send_scheduled_message(schedule)
            else:
                print("====================================")
                print("Kunlar mos kelmaydi")
                print("====================================")


def send_scheduled_message(schedule):
    for group in schedule.groups.all():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_message(
                schedule.channel.channel_id, schedule.message_id, group.group_id
            )
        )
