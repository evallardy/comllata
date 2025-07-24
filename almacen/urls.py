from django.urls import path
from .views import (
    InventarioListView,
    InventarioCreateView,
    InventarioUpdateView,
    InventarioDeleteView,
)

urlpatterns = [
    path('inventario/', InventarioListView.as_view(), name='inventario_list'),
    path('inventario/nuevo/', InventarioCreateView.as_view(), name='inventario_create'),
    path('inventario/<int:pk>/editar/', InventarioUpdateView.as_view(), name='inventario_update'),
    path('inventario/<int:pk>/eliminar/', InventarioDeleteView.as_view(), name='inventario_delete'),
]
