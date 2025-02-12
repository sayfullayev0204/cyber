from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TelegramUser, Group, TelegramMessageLog, Domains
from .serializers import UserSerializer, GroupSerializer, MessageSerializer
from .forms import DomainForm
from django.shortcuts import redirect,render

class SaveMessageView(APIView):
    def post(self, request):
        data = request.data

        group_id = data.get('group', {}).get('chat_id')
        group_name = data.get('group', {}).get('title')
        user_id = data.get('user', {}).get('telegram_id')
        username = data.get('user', {}).get('username')
        message_id = data.get('message_id')
        text = data.get('text', "")
        file_type = data.get('file_type', "")

        if not (group_id and user_id and message_id):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Guruhni bazadan olish yoki yaratish
        group, created = Group.objects.get_or_create(
            group_id=group_id, defaults={"name": group_name, "category": None}
        )

        # Xabarni bazaga saqlash
        message = TelegramMessageLog.objects.create(
            group=group,
            user_id=user_id,
            username=username,
            message_id=message_id,
            text=text,
            file_type=file_type
        )

        return Response({"message": "Data saved successfully"}, status=status.HTTP_201_CREATED)


class DomainListView(APIView):
    def get(self, request):
        domains = Domains.objects.all().values_list('domain_suffix', flat=True)
        return Response(domains, status=status.HTTP_200_OK)

def domain_list(request):
    domains = Domains.objects.all()
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_domain')
    else:
        form = DomainForm()
    return render(request, 'check/list_domain.html', {'domains': domains, 'form': form})

def message_list(request):
    messages = TelegramMessageLog.objects.all()
    return render(request, 'check/telegram_message.html',{'message':messages})