from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.db import models
from django.contrib.auth.models import AbstractUser

from taller.models import Taller

class Usuario(AbstractUser):
    materno = models.CharField(max_length=50, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    is_taller = models.BooleanField('Taller', blank=True, null=True, default=False)
    is_cliente = models.BooleanField('Cliente', blank=True, null=True, default=False)
    empresa = models.ForeignKey(Taller, to_field='id_empresa', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario_taller')
#    taller = models.ForeignKey(Taller, on_delete=models.SET_NULL, null=True, blank=True)
    notificar = models.BooleanField('Notificaciones', blank=True, null=True, default=False)
    
    class Meta:
        db_table = 'Usuario'
        verbose_name = 'Usuario' 
        verbose_name_plural = 'Usuarios' 
        ordering = ['last_name', 'materno', 'first_name']
        permissions = (
            ('usuarios', 'Consulta usuarios'),
        )

