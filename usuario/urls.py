from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import *

urlpatterns = [
    # Login para clientes
    path('', CustomLoginView.as_view(
        template_name='registration/cliente/login.html',
        redirect_authenticated_user=True
    ), name='login_cliente'),

    # Login para administradores
    path('administracion/', CustomLoginView.as_view(
        template_name='registration/adminis/login.html',
        redirect_authenticated_user=True
    ), name='login_admin'),

     # Logout personalizado
     path('logout/', custom_logout_view, name='logout'),

     # Vista post-login para redirección
     path('usuarios/', usuarios.as_view(), name='usuarios'),
     path('registro/', RegistroUsuarioView.as_view(), name='registro'),
     path('mod_usuario/<pk>/', UserUpdateView.as_view(), name='mod_usuario'),
     path('cambiar_contrasena/', Cambiar_contrasena.as_view(), name='cambiar_contrasena'), 
     path('permisos_usuario/', Permisos_usuario.as_view(), name='accesos'),
     path('todos_permisos/<id>/', todos_permisos, name='todos_permisos'),
     path('registrarse/', registrarse, name='registrarse'),
]
