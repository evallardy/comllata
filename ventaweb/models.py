from django.db import models
from usuario.models import Usuario

class Venta(models.Model):
    comprador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_order_id = models.CharField(max_length=100, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Venta #{self.id} - {self.nombre_cliente}'
    
    class Meta:
        verbose_name = 'Venta' 
        verbose_name_plural = 'Ventas' 
        ordering = ['-fecha','paypal_order_id']
        db_table = 'Venta'
