# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("", TalleresView.as_view(), name="importacion"),
    path("talleres/", talleres, name="importa_talleres"),
    path("llantas/", llantas, name="importa_llantas"),
    path("actualiza/", actualizaInventario, name="actualiza_inventario"),
    path("promociones/", TalleresView.as_view(), name="importa_promociones"),
]
