from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuario/', include('usuario.urls')),
    path('importacion/', include('importacion.urls')),
    path('ventaweb/', include('ventaweb.urls')),
]
