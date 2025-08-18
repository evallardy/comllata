# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("", Venta.as_view(), name="venta"),
    path('ffiltrar_combos/', filtrar_combos, name='filtrar_combos'),
    path('filtrar_llantas/', filtrar_llantas, name='filtrar_llantas'),
    path('paypal/registrar/', RegistrarVentaPaypalView.as_view(), name='registrar_venta_paypal'),
    path('ventas/', PedidoDetalleListView.as_view(), name='lista_ventas'),
    path('entregadas/', EntregaDetalleListView.as_view(), name='lista_entregadas'),
    path('ventas/surtir/<int:venta_id>/', SurtirVentaView.as_view(), name='surtir_venta'),
    path('prueba_envio/<int:venta_id>/', pruebaEnvio, name='prueba_envio'),
    path('verificar-codigo/', verificar_codigo_entrega, name='verificar_codigo'),
    path('ventas/', VentaDetalleListView.as_view(), name='venta_list_comision'),
    path('ventas/<int:pk>/', VentaDetalleDetailView.as_view(), name='venta_detail_comision'),
    path('ventas/pagar-comision/', PagarComisionView.as_view(), name='pagar_comision'),
    path("reglas/", ReglasComisionList.as_view(), name="reglas_list"),
    path("reglas/nueva/", ReglasComisionCreate.as_view(), name="reglas_create"),
    path("reglas/<int:pk>/editar/", ReglasComisionUpdate.as_view(), name="reglas_update"),
    path("reglas/<int:pk>/borrar/", ReglasComisionDelete.as_view(), name="reglas_delete"),
]
