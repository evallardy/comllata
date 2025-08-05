# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("", Venta.as_view(), name="venta"),
    path('ffiltrar_combos/', filtrar_combos, name='filtrar_combos'),
    path('filtrar_llantas/', filtrar_llantas, name='filtrar_llantas'),
    path('paypal/registrar/', RegistrarVentaPaypalView.as_view(), name='registrar_venta_paypal'),
    path('ventas/', VentaDetalleListView.as_view(), name='lista_ventas'),
    path('entregadas/', EntregaDetalleListView.as_view(), name='lista_entregadas'),
    path('ventas/surtir/<int:venta_id>/', SurtirVentaView.as_view(), name='surtir_venta'),
]
