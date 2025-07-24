from django.urls import path
from .views import *

urlpatterns = [
    path('', BuscarLlantaView.as_view(), name='home'),
    path("administracion/", AdministracionView.as_view(), name="administracion"),
    path("importacion/", ImportacionView.as_view(), name="importacion"),
    path("actualizacion/", ActualizacionView.as_view(), name="actualizacion"),
    path("actualiza/", actualiza, name="actualiza"),
]