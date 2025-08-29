from django.db import models

from usuario.models import Usuario
from taller.models import Taller


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
ESTATUS_COMISION = (
    (0, 'No aplicó comisión'),
    (1, 'Por pagar'),
    (2, 'Para depósito'),
    (3, 'Depositado'),
)

class VentaDetalle(models.Model):
    venta = models.ForeignKey(VentaPaypal, on_delete=models.CASCADE, related_name='detalles')
    id_inventario = models.CharField("Id primario",max_length=64, blank=True, null=True)
    empresa = models.ForeignKey(Taller, to_field='id_empresa', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    razon_social = models.CharField("Rasón social",max_length=100, blank=True, null=True)
    descripcion = models.CharField('Descripción', max_length=255)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2, default=0)
    precio_unitario_s_iva = models.DecimalField('Precio unitario s/iva', max_digits=10, decimal_places=2, default=0)
    importe = models.DecimalField('Importe', max_digits=12, decimal_places=2)
    estatus = models.IntegerField('Estatus', choices=ESTATUS, default=0)
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Usuario')
    fecha_pedido = models.DateTimeField('Pedido', auto_now_add=True,blank=True, null=True)
    fecha_entrega = models.DateTimeField('Entrega', blank=True, null=True)
    fecha_pago_comision = models.DateTimeField('Pago comisión', blank=True, null=True)
    token_hash = models.CharField(max_length=200, blank=True, null=True)
    estatus_comision = models.IntegerField('Estatus', choices=ESTATUS_COMISION, default=0)
    deposito = models.DecimalField('Deposito', max_digits=10, decimal_places=2, default=0)
    comision = models.DecimalField('Comisión', max_digits=10, decimal_places=2, default=0)
    porcentaje = models.DecimalField('Porcentaje', max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.descripcion} ({self.cantidad})"
    
    class Meta:
        verbose_name = 'Detalle' 
        verbose_name_plural = 'Detalles' 
        ordering = ['venta', 'empresa', 'id_inventario']
        db_table = 'VentaDetalle'

ESTATUS_REGLA = (
    (0, 'Vencida'),
    (1, 'Vigente'),
)
TIPO_COMISION = (
    (0, 'Porcentaje'),
    (1, 'Monto'),
)
TALLERES = (
    (False, ''),
    (True, 'Todos'),
)
class ReglasComision(models.Model):
    talleres = models.BooleanField('Talleres', choices=TALLERES, default=False)
    empresa = models.ForeignKey(Taller, to_field='id_empresa', on_delete=models.SET_NULL, null=True, blank=True, related_name='reglas')
    marca = models.CharField("Marca",max_length=100, blank=True, null=True)
    rin = models.DecimalField("Rin", decimal_places=2, max_digits=10, default=0, blank=True, null=True)
    tipo = models.IntegerField('Tipo', choices=TIPO_COMISION, default=0, blank=True, null=True)
    cantidad = models.DecimalField('Cantidad', max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    estatus = models.IntegerField('Estatus', choices=ESTATUS_REGLA, default=1)
    fecha_inicial = models.DateField('Inicia', blank=True, null=True)
    fecha_final = models.DateField('Termina', blank=True, null=True)
    creado = models.DateTimeField("Creado", auto_now=True, blank=True, null=True)
    modificado = models.DateTimeField("Creado", auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.id_inventario} ({self.ancho})/({self.alto}) ({self.rin}) {self.empresa.razon_social} {self.get_tipo_display} ({self.cantidad})"
    
    class Meta:
        verbose_name = 'Regla' 
        verbose_name_plural = 'Reglas' 
        ordering = ['fecha_inicial', 'fecha_final']
        db_table = 'ReglasComision'

