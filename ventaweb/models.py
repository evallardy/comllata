from django.db import models

from usuario.models import Usuario


class VentaPaypal(models.Model):
    comprador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_order_id = models.CharField(max_length=100, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    nombre_completo = models.CharField(max_length=200, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    cp = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=10, blank=True)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True, blank=True)


    def __str__(self):
        return f'Venta #{self.id} - {self.nombre_cliente}'
    
    class Meta:
        verbose_name = 'Venta' 
        verbose_name_plural = 'Ventas' 
        ordering = ['-fecha','paypal_order_id']
        db_table = 'Venta'

ESTATUS = (
    (0, 'Por surtir'),
    (1, 'Surtido'),
)

class VentaDetalle(models.Model):
    venta = models.ForeignKey(VentaPaypal, on_delete=models.CASCADE, related_name='detalles')
    id_inventario = models.CharField("Id primario",max_length=64, blank=True, null=True)
    id_empresa = models.CharField("Id empresa",max_length=64, blank=True, null=True)
    descripcion = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    estatus = models.IntegerField('Estatus', choices=ESTATUS, default=0)
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Usuario')
    fecha_pedido = models.DateTimeField('Pedido', auto_now_add=True,blank=True, null=True)
    fecha_entrega = models.DateTimeField('Entrega', auto_now=True ,blank=True, null=True)
    token_hash = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.descripcion} ({self.cantidad})"
    
    class Meta:
        verbose_name = 'Detalle' 
        verbose_name_plural = 'Detalles' 
        ordering = ['venta', 'id_empresa', 'id_inventario']
        db_table = 'VentaDetalle'
