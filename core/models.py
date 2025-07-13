from django.db import models

ACTIVO = (
    (False, 'No'),
    (True, 'Si'),
)

class Aviso(models.Model):
    aviso = models.CharField("Aviso",max_length=255)
    fecha_inicial = models.DateField('Inicia prom.')
    fecha_final = models.DateField('finaliza prom.')
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Aviso' 
        verbose_name_plural = 'Avisos' 
        ordering = ['fecha_inicial']
        db_table = 'Aviso'

class Vehiculo(models.Model):
    nombre = models.CharField("Vehículo",max_length=60)
    estatus = models.BooleanField('Activo', choices=ACTIVO, default=True)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Vehículo' 
        verbose_name_plural = 'Vehículos' 
        ordering = ['nombre']
        unique_together= ['nombre']
        db_table = 'Vehiculo'

class Menu(models.Model):
    menu = models.CharField("Menú",max_length=100)
    estatus = models.BooleanField('Activo', choices=ACTIVO, default=True)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Menú' 
        verbose_name_plural = 'Menús' 
        ordering = ['menu']
        unique_together= ['menu']
        db_table = 'Menu'

class MenuOpciones(models.Model):
    menus = models.ForeignKey(Menu, on_delete=models.CASCADE)
    orden = models.IntegerField("Orden visual",default=1)
    descripcion = models.CharField("texto menú",max_length=60)
    imagen = models.CharField("Imagen menú",max_length=100)
    url = models.CharField("Url",max_length=100)
    estatus = models.BooleanField('Activo', choices=ACTIVO, default=True)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = 'Opción' 
        verbose_name_plural = 'Opciones' 
        ordering = ['menus','orden']
        unique_together= ['menus','orden']
        db_table = 'MenuOpciones'
