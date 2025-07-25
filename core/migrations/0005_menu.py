# Generated by Django 4.0.4 on 2025-07-07 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_vehiculo_estatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('menu', models.CharField(max_length=100, verbose_name='Menú')),
                ('orden', models.IntegerField(default=1, max_length=60, verbose_name='Orden visual')),
                ('descripcion', models.CharField(max_length=60, verbose_name='texto menú')),
                ('imagen', models.CharField(max_length=100, verbose_name='Imagen menú')),
                ('url', models.CharField(max_length=100, verbose_name='Url')),
                ('estatus', models.BooleanField(choices=[(False, 'No'), (True, 'Si')], default=True, verbose_name='Activo')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='Actualizado')),
            ],
            options={
                'verbose_name': 'Menú',
                'verbose_name_plural': 'Menús',
                'db_table': 'Menu',
                'ordering': ['menu', 'orden'],
                'unique_together': {('menu', 'orden')},
            },
        ),
    ]
