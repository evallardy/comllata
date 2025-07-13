from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

ES_CLIENTE = (
    (False, 'No'),
    (True, 'Si'),
)

class Usuario(AbstractUser):
    materno = models.CharField(max_length=50, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'Usuario'
        permissions = (
            ('usuarios', 'Consulta usuarios'),
        )

