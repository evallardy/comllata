from django.urls import path
from .views import *

urlpatterns = [
    path('', BuscarLlantaView.as_view(), name='home'),
    path("administracion/", AdministracionView.as_view(), name="administracion"),
    path("importacion/", ImportacionView.as_view(), name="importacion"),
    path("actualizacion/", ActualizacionView.as_view(), name="actualizacion"),
    path("actualiza/", actualiza, name="actualiza"),
    path('avisos/', AvisoListView.as_view(), name='aviso_list'),
    path('avisos/nuevo/', AvisoCreateView.as_view(), name='aviso_create'),
    path('avisos/editar/<int:pk>/', AvisoUpdateView.as_view(), name='aviso_update'),
    path('avisos/eliminar/<int:pk>/', AvisoDeleteView.as_view(), name='aviso_delete'),
    path('carrito/', Carrito.as_view(), name='carrito'),
    path('about/', About.as_view(), name='about'),
    path('contact/', Contact.as_view(), name='contact'),
    path('muestraProductos/', MuestraProductos.as_view(), name='muestraProductos'),
    path('muestraTaller/<int:pk>/', MuestraTaller.as_view(), name='muestraTaller'),
    path('muestraProductosTaller/<pk>/',MuestraProductosTaller.as_view(), name='muestraProductosTaller'),
    path('agrega_carrito/<int:pk>/',agrega_carrito, name='agregaCarrito'),
    path('agrega_carrito_cantidad/<int:pk>/<int:cantidad>/',agrega_carrito_cantidad, name='agregaCarritoCantidad'),
    path('carrito/eliminar/<int:pk>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', vaciar_carrito, name='vaciar_carrito'),
]