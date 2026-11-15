from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# Include all API routes and serve media files in debug mode.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("geom_challenges.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
