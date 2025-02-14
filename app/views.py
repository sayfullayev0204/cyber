from datetime import datetime
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from app.models import BotToken
from app.models import Channel, Group, ScheduledMessages, WeekDays
from app.tasks import send_message_task
from .forms import UserRegisterForm, UserEditForm, GroupForm, ChannelForm, BotTokenForm
import logging

from for_bot.models import TelegramMessageLog

logger = logging.getLogger(__name__)


# start with celey
def send_message_to_groups(channel_id, message_id, group_ids):
    for group_id in group_ids:
        send_message_task.delay(channel_id, message_id, group_id)


import logging


def send_message(request):
    if request.method == "POST":
        channel_id = request.POST.get("channel_id")
        message_id = request.POST.get("message_id")
        group_ids = request.POST.getlist("group_ids")
        schedule_type = request.POST.get("schedule_type")
        title = request.POST.get("title")

        if not all([channel_id, message_id, group_ids, schedule_type]):
            messages.error(request, "Barcha maydonlarni to'ldiring!")
            return redirect("send_message_page")

        try:
            channel = Channel.objects.get(channel_id=channel_id)
            scheduled_message = ScheduledMessages.objects.create(
                channel=channel,
                message_id=message_id,
                schedule_type=schedule_type,
                title=title,
            )

            if schedule_type == "daily":
                scheduled_message.day_date = request.POST.get("day_date")
                scheduled_message.day_time = request.POST.get("day_time")
            elif schedule_type == "repedly":
                if request.POST.get("schedule_subtype") == "daily":
                    scheduled_message.repetly_time = request.POST.get(
                        "weekly_repetly_time"
                    )
                    start_day = request.POST.get("start_day")
                    end_day = request.POST.get("end_day")
                    scheduled_message.start_day = start_day
                    scheduled_message.end_day = end_day
                elif request.POST.get("schedule_subtype") == "weekly":
                    scheduled_message.repetly_time = request.POST.get("repetly_time")
                    days = WeekDays.objects.filter(
                        name__in=request.POST.getlist("weekdays[]")
                    )
                    scheduled_message.weekly_days.set(days)

            scheduled_message.groups.set(Group.objects.filter(group_id__in=group_ids))
            scheduled_message.save()

            if schedule_type == "onetime":
                try:
                    # send_message_to_groups(channel_id, message_id, group_ids)
                    messages.success(request, "Xabar yuborildi!")
                except Exception as exc:
                    logging.error(f"Error sending message: {exc}")
                    messages.error(request, f"Xatolik yuz berdi: {exc}")
            else:
                messages.success(request, "Xabar jadvalga qo'shildi!")

            return redirect("send_message_page")

        except Channel.DoesNotExist:
            messages.error(request, "Kanal topilmadi!")
        except Exception as exc:
            logging.error(f"Error in send_message: {exc}")
            messages.error(request, f"Xatolik yuz berdi: {exc}")

    return render(request, "index.html")


@login_required
def send_message_page(request):
    if request.user.role in ["superuser", "postmaker"]:
        days = WeekDays.objects.all()
        channels = Channel.objects.all()
        groups = Group.objects.all()
        scheduled_messages = ScheduledMessages.objects.all().order_by("-created_at")
        telegrammessages = TelegramMessageLog.objects.all().count()
        return render(
            request,
            "index.html",
            {
                "channels": channels,
                "groups": groups,
                "scheduled_messages": scheduled_messages,
                "days": days,
            },
        )
    else:
        return redirect("home")


# end with celery


@login_required
def list(request):
    if request.user.role in ["superuser", "postmaker"]:
        list = ScheduledMessages.objects.prefetch_related("groups").all()
        return render(request, "list.html", {"list": list})
    else:
        return redirect("home")


@login_required
def register_view(request):
    if request.user.role in ["superuser"]:  # Faqat superuser va postmakerlarga ruxsat
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect("home")
        else:
            form = UserRegisterForm()
        return render(request, "accounts/register.html", {"form": form})

    return redirect("home")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(
                request,
                "accounts/login.html",
                {"error": "Invalid username or password"},
            )
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def edit_account_view(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = UserEditForm(instance=request.user)
    return render(request, "accounts/edit_account.html", {"form": form})


@login_required
def home(request):
    groups = Group.objects.all()
    channels = Channel.objects.all()
    days = WeekDays.objects.all()
    channels = Channel.objects.all()
    groups = Group.objects.all()
    gorup_count = groups.count()
    scheduled_messages = ScheduledMessages.objects.all().order_by("-created_at")
    scheduled_messages_count = ScheduledMessages.objects.all().count()
    telegrammessages = TelegramMessageLog.objects.all().count()
    send_messages = ScheduledMessages.objects.filter(schedule_type="onetime").count()

    if request.method == "POST":
        if "delete_group_id" in request.POST:
            group_id = request.POST.get("delete_group_id")
            group = get_object_or_404(Group, id=group_id)
            group.delete()
        elif "delete_channel_id" in request.POST:
            channel_id = request.POST.get("delete_channel_id")
            channel = get_object_or_404(Channel, id=channel_id)
            channel.delete()
        return redirect("home")

    return render(request, "home.html", {"groups": groups, "channels": channels,"gorup_count":gorup_count,"scheduled_messages_count":scheduled_messages_count,"telegrammessages":telegrammessages,"send_messages":send_messages})


@login_required
def edit_group(request, group_id):
    if request.user.role in ["superuser"]:
        group = get_object_or_404(Group, id=group_id)
        if request.method == "POST":
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                return redirect("home")
        else:
            form = GroupForm(instance=group)
        return render(request, "edit.html", {"form": form})
    else:
        return redirect("home")


@login_required
def edit_channel(request, channel_id):
    if request.user.role in ["superuser"]:
        channel = get_object_or_404(Channel, id=channel_id)
        if request.method == "POST":
            form = ChannelForm(request.POST, instance=channel)
            if form.is_valid():
                form.save()
                return redirect("home")
        else:
            form = ChannelForm(instance=channel)
        return render(request, "edit.html", {"form": form})
    else:
        return redirect("home")

@login_required
def create_group(request):
    if request.user.role in ["superuser"]:
        if request.method == "POST":
            form = GroupForm(request.POST)
            if form.is_valid():
                group_id = form.cleaned_data["group_id"]
                if Group.objects.filter(group_id=group_id).exists():
                    messages.error(request, "Bu group_id allaqachon mavjud.")
                else:
                    form.save()
                    return redirect("home")
        else:
            form = GroupForm()
        return render(request, "create.html", {"form": form, "group": "group"})
    else:
        return redirect("home")


@login_required
def create_channel(request):
    if request.user.role in ["superuser"]:
        if request.method == "POST":
            form = ChannelForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("home")
        else:
            form = ChannelForm()
        return render(request, "create.html", {"form": form, "channel": "channel"})
    else:
        return redirect("home")


@login_required
def edit_bot(request):
    if request.user.role in ["superuser"]:
        bot_token = BotToken.objects.first()

        if request.method == "POST":
            form = BotTokenForm(request.POST, instance=bot_token)
            if form.is_valid():
                BotToken.objects.all().delete()
                form.save()
                return redirect("home")
        else:
            form = BotTokenForm(instance=bot_token)

        return render(request, "manage_token.html", {"form": form})
    else:
        return redirect("home")

import requests
from django.conf import settings

def get_bot_token():
    bot_config = BotToken.objects.first()
    if bot_config:
        return bot_config.token
    raise ValueError("Bot token topilmadi! Iltimos, bazaga token qo'shing.")


TELEGRAM_BOT_TOKEN=get_bot_token()

def get_bot_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["result"]["id"]
    return None

TELEGRAM_BOT_ID = get_bot_id()

def check_bot_groups():
    """
    Telegram API orqali bot qaysi guruhlarga a’zo ekanligi va admin emasligini tekshiradi.
    """
    groups = Group.objects.all()
    non_admin_groups = []

    for group in groups:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatAdministrators?chat_id={group.group_id}"
        response = requests.get(url)

        if response.status_code == 200:
            admins = response.json().get("result", [])
            bot_is_admin = any(admin["user"]["id"] == int(TELEGRAM_BOT_ID) for admin in admins)

            if not bot_is_admin:  # Agar bot admin bo‘lmasa
                group.is_admin = False
                non_admin_groups.append(group)
            else:
                group.is_admin = True
            group.save()

    return non_admin_groups

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Group

@login_required
def show_non_admin_groups(request):
    if request.user.role == "superuser":
        non_admin_groups = check_bot_groups()

        if request.method == "POST":
            group_ids = request.POST.getlist("group_ids")
            Group.objects.filter(group_id__in=group_ids).delete()
            messages.success(request, "Tanlangan guruhlar o‘chirildi.")
            return redirect("show_non_admin_groups")

        return render(request, "non_admin_groups.html", {"groups": non_admin_groups})
    else:
        return redirect("home")
