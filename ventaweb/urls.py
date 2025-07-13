# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("", Venta.as_view(), name="venta"),
    path('ffiltrar_combos/', filtrar_combos, name='filtrar_combos'),
    path('filtrar_llantas/', filtrar_llantas, name='filtrar_llantas'),
    
]
