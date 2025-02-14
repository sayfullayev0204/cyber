from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from for_bot.views import SaveMessageView, DomainListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("api/save_message/", SaveMessageView.as_view(), name="save_message"),
    path("api/domains/", DomainListView.as_view(), name="domain_list"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
