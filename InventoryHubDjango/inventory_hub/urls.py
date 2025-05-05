from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index
from inventory.views import about

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
    path('employee/', include('employee.urls')),
    path('about/', about, name='about'),
    path('', index, name='index'),
    # Removed attendance and face_attendance URL patterns that were causing errors
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)