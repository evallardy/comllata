from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuario/', include('usuario.urls')),
    path('importacion/', include('importacion.urls')),
    path('taller/', include('taller.urls')),
    path('almacen/', include('almacen.urls')),
    path('ventaweb/', include('ventaweb.urls')),
#    path('accounts/', include('django.contrib.auth.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
