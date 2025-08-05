from django.urls import path
from .views import *

urlpatterns = [
    path('talleres/', TallerListView.as_view(), name='taller_list'),
    path('talleres/nuevo/', TallerCreateView.as_view(), name='taller_create'),
    path('talleres/<int:pk>/editar/', TallerUpdateView.as_view(), name='taller_update'),
    path('talleres/<int:pk>/eliminar/', TallerDeleteView.as_view(), name='taller_delete'),
]