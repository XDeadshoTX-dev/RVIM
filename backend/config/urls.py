from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import about_view, help_view

urlpatterns = [
    path("django-admin/", admin.site.urls),

    # ЛР1: Статичні сторінки
    path("about/", about_view, name="about"),
    path("help/", help_view, name="help"),

    # API
    path("api/auth/", include("apps.accounts.urls")),
    path("api/todo/", include("apps.todo.urls")),

    # ЛР3: OpenAPI / Swagger документація
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]