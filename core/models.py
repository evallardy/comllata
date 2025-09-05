from django.db import models
from django.utils import timezone

ACTIVO = (
    (False, 'No'),
    (True, 'Si'),
)

ICONOS = (
    ('transporte', '🚚 Transporte'),
    ('dinero', '💰 Dinero'),
    ('regalo', '🎁 Regalo'),
)

TIPO = (
    (0, 'Clientes'),
    (1, 'Talleres'),
    (2, 'Administradores'),
)

class PromocionEspecial(models.Model):
    titulo = models.CharField("Titulo", max_length=255, blank=True, null=True)
    texto = models.CharField("Texto", max_length=255, blank=True, null=True)
    detalle = models.CharField("Detalle", max_length=255, blank=True, null=True)
    mas_detalle = models.TextField("Más detalle", blank=True, null=True)
    fecha_inicial = models.DateTimeField('Inicia prom.', blank=True, null=True)
    fecha_final = models.DateTimeField('Finaliza prom.', blank=True, null=True)

    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        ordering = ['titulo', 'texto','fecha_inicial']
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        db_table = 'PromocionEspecial'

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicial} - {self.fecha_final})"

class Recomendacion(models.Model):
    titulo = models.CharField("Título", max_length=255, blank=True, null=True)
    mensaje = models.CharField("Mensaje", max_length=255, blank=True, null=True)
    imagen = models.ImageField('Imagen', upload_to='recomendaciones/', blank=True, null=True)

    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        ordering = ['titulo', 'mensaje']
        verbose_name = "Recomendación"
        verbose_name_plural = "Recomendaciones"
        db_table = 'Recomendacion'

    def __str__(self):
        return f"{self.Titulo} - {self.mensaje}"

    @property
    def is_activo(self):
        """Retorna True si hoy está dentro del rango de fechas"""
        hoy = timezone.now().date()
        return self.fecha_inicial <= hoy <= self.fecha_final

class Aviso(models.Model):
    tipo = models.IntegerField('Tipo', choices=TIPO, default=0)
    aviso = models.CharField("Aviso", max_length=255)
    icono = models.CharField('Ícono', max_length=80, choices=ICONOS, default=1)
    fecha_inicial = models.DateField('Inicia prom.', blank=True, null=True)
    fecha_final = models.DateField('Finaliza prom.', blank=True, null=True)

    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True)
    modificado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        ordering = ['tipo', 'fecha_inicial']
        verbose_name = "Aviso"
        verbose_name_plural = "Avisos"
        db_table = 'Aviso'

    def __str__(self):
        return f"{self.aviso} ({self.fecha_inicial} - {self.fecha_final})"

    @property
    def is_activo(self):
        """Retorna True si hoy está dentro del rango de fechas"""
        hoy = timezone.now().date()
        return self.fecha_inicial <= hoy <= self.fecha_final

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
