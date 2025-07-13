from django.urls import path

from .views import *

urlpatterns = [
     path('usuarios/', usuarios.as_view(), name='usuarios'),
     path('registro/', registro, name='registro'),
     path('mod_usuario/<pk>/', UserUpdateView.as_view(), name='mod_usuario'),
     path('cambiar_contrasena/', Cambiar_contrasena.as_view(), name='cambiar_contrasena'), 
     path('permisos_usuario/', Permisos_usuario.as_view(), name='accesos'),
     path('todos_permisos/<id>/', todos_permisos, name='todos_permisos'),
]
