from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path("actualizar_llantas/", ActualizarLlantasView.as_view(), name="actualizar_llantas"),
    path("buscar_llanta/", BuscarLlantaView.as_view(), name="buscar_llanta"),
]