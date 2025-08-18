from django.db import models

ESTATUS = (
    (0, 'Existe'),
    (1, 'Nuevo'),
    (2, 'Modificado'),
    (3, 'Sin recepción'),
)

class Taller(models.Model):
    id_empresa = models.CharField("Id empresa", max_length=64, unique=True)  # único
#    id_empresa = models.CharField("Id empresa",max_length=64, blank=True, null=True)
    razon_social = models.CharField("Rasón social",max_length=100, blank=True, null=True)
    direccion = models.CharField("Dirección",max_length=256, null=True, blank=True)
    numero_exterior = models.CharField("Núm. ext.",max_length=20, null=True, blank=True)
    numero_interior = models.CharField("Núm. ext.",max_length=20, null=True, blank=True)
    id_colonia = models.CharField("Id colonia",max_length=40, null=True, blank=True)
    colonia = models.CharField("Colonia",max_length=100, null=True, blank=True)
    codigo_postal = models.CharField("Código postal",max_length=100, null=True, blank=True)
    id_municipio = models.CharField("Id municipio",max_length=40, null=True, blank=True)
    municipio = models.CharField("Municipio",max_length=100, null=True, blank=True)
    id_estado = models.CharField("Id estado",max_length=40, null=True, blank=True)
    estado = models.CharField("Estado",max_length=100, null=True, blank=True)
    telefono = models.CharField("Teléfono",max_length=40, null=True, blank=True)
    longitud = models.CharField("Longitud",max_length=100, null=True, blank=True)
    latitud = models.CharField("Latitud",max_length=100, null=True, blank=True)
    estatus = models.IntegerField("Estatus", choices=ESTATUS, default=1)
    # Bitácora
    creado = models.DateTimeField("Creado", auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return '%s' % (self.razon_social)

    @property
    def estatus_nombre(self):
        return self.get_estatus_display()

    class Meta:
        verbose_name = 'Taller' 
        verbose_name_plural = 'Talleres' 
        ordering = ['razon_social']
        unique_together= ['razon_social']
        db_table = 'Taller'
