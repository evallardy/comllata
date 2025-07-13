from django.db import models

from taller.models import Taller, ESTATUS, ACTUALIZADO

class MarcaLlanta(models.Model):
    nombre = models.CharField("Marca",max_length=100)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Marca' 
        verbose_name_plural = 'Marcas' 
        ordering = ['nombre']
        unique_together= ['nombre']
        db_table = 'MarcaLlanta'

class Llanta(models.Model):
    marca = models.ForeignKey(MarcaLlanta, on_delete=models.CASCADE, blank=True, null=True)
    modelo = models.CharField("Modelo",max_length=80, blank=True, null=True)
    ancho = models.CharField("Ancho",max_length=10, blank=True, null=True)
    alto = models.CharField("Alto",max_length=10, blank=True, null=True)
    rin = models.CharField("Rin",max_length=10, blank=True, null=True)
    radial = models.IntegerField("Radial", default=0)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True, blank=True, null=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Llanta' 
        verbose_name_plural = 'Llantas' 
        ordering = ['marca','modelo','ancho','alto','rin']
        unique_together= [('marca','modelo','ancho','alto','rin')]
        db_table = 'Llanta'

class Inventario(models.Model):
    id_inventario = models.CharField("Id primario",max_length=64, blank=True, null=True)
    id_empresa = models.CharField("Id empresa",max_length=64, blank=True, null=True)
    talleres = models.ForeignKey(Taller, on_delete=models.CASCADE, blank=True, null=True)
    llantas = models.ForeignKey(Llanta, on_delete=models.CASCADE, blank=True, null=True)
    producto_clave = models.CharField("Producto/Clave",max_length=100, blank=True, null=True)  #SKU
    descripcion = models.CharField("Descripción", max_length=255, blank=True, null=True)
    ancho = models.DecimalField("Ancho", decimal_places=2, max_digits=10, default=0)
    alto = models.DecimalField("Alto", decimal_places=2, max_digits=10, default=0)
    rin = models.DecimalField("Rin", decimal_places=2, max_digits=10, default=0)
    existencia = models.IntegerField("Existencia", default=0)
    precio = models.DecimalField("Precio", decimal_places=2, max_digits=10, default=0)
    actualizado = models.IntegerField("Actualizado", choices=ACTUALIZADO, default=False)
    estatus = models.IntegerField("Estatus", choices=ESTATUS, default=1)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True, blank=True, null=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    @property
    def estatus_nombre(self):
        return self.get_estatus_display()

    class Meta:
        verbose_name = 'Llanta' 
        verbose_name_plural = 'Llantas' 
        ordering = ['talleres','producto_clave']
#        unique_together= [('talleres','producto_clave'),('talleres','llantas')]
        db_table = 'Inventario'

class Entradas(models.Model):
    talleres = models.ForeignKey(Taller, on_delete=models.CASCADE, blank=True, null=True)
    llantas = models.ForeignKey(Llanta, on_delete=models.CASCADE, blank=True, null=True)
    producto_clave = models.CharField("Producto/Clave",max_length=100, blank=True, null=True)
    precio = models.DecimalField("Precio venta", decimal_places=2, max_digits=10, default=0)
    cantidad = models.IntegerField("Cantidad", default=0)

    class Meta:
        verbose_name = 'Entrada' 
        verbose_name_plural = 'Entradas' 
        ordering = ['talleres','producto_clave']
        db_table = 'Entrada'

