from django.contrib import admin
from django.urls import path, include
from teulang import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("articles/", include("articles.urls")),
]

# 개발 중에만 media root 아래와 같이 설정.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
