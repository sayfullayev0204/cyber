from django.urls import path
from . import views
from for_bot.views import domain_list, message_list

urlpatterns = [
    path("send-message/", views.send_message, name="send_message"),
    path("send/", views.send_message_page, name="send_message_page"),
    path("", views.home, name="home"),
    path("messages/", views.list, name="list"),
    path("register/", views.register_view, name="register"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("edit-account/", views.edit_account_view, name="edit_account"),
    path("group/create/", views.create_group, name="create_group"),
    path("channel/create/", views.create_channel, name="create_channel"),
    path("group/<int:group_id>/edit/", views.edit_group, name="edit_group"),
    path("channel/<int:channel_id>/edit/", views.edit_channel, name="edit_channel"),
    path("edit-bot/", views.edit_bot, name="edit_bot"),
    path("domains/", domain_list, name="add_domain"),
    path("chek-message", message_list, name="chek_message"),

    path("non-admin-groups/", views.show_non_admin_groups, name="show_non_admin_groups"),
]

