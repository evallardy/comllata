# views.py
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.conf import settings
import requests
import json
from django.db import connection
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal

from taller.models import *
from almacen.models import *

class TalleresView(TemplateView):
    template_name = "importacion/pagina.html"

@require_POST
@csrf_exempt
def talleres(request):
    if request.method == "POST":
        url = settings.URL_TALLERES
        headers = { "Authorization": settings.TOKEN_BOT }
        response = requests.get(url, headers=headers)

        context = {
            "talleres": [],
            "conta_nuevos": 0,
            "conta_existen": 0,
            "conta_modificados": 0
        } 

        if response.status_code == 200:
            data = response.json()  # Usa directamente .json()
            leidos = 0
            actualizados = 0
            nuevos = 0
            sin_modificacion = 0
            with transaction.atomic():
                Taller.objects.all().update(estatus=3)  # Cuidado si la tabla es grande

                for dato in data['data']['rows']:
                    leidos += 1
                    taller = Taller.objects.filter(id_empresa=dato['id']).first()
                    if taller:
                        if (
                            taller.id_estado == dato['stateId'] and
                            taller.id_municipio == dato['cityId'] and
                            taller.id_colonia == dato['neighborhoodId'] and
                            taller.razon_social == dato['name'] and
                            taller.telefono == dato['phone'] and
                            taller.estado == dato['state'] and
                            taller.municipio == dato['city'] and
                            taller.colonia == dato['neighborhood'] and
                            taller.codigo_postal == dato['postalCode'] and
                            taller.numero_exterior == dato['exteriorNumber'] and
                            taller.numero_interior == dato['interiorNumber'] and
                            taller.direccion == dato['street'] and
                            taller.longitud == dato['latitude'] and
                            taller.latitud == dato['longitude']
                            ):
                            taller.estatus = 0
                            taller.save()
                            sin_modificacion += 1
                        else:
                            taller.razon_social = dato['name']
                            taller.direccion = dato['street']
                            taller.numero_exterior = dato['exteriorNumber']
                            taller.numero_interior = dato['interiorNumber']
                            taller.id_colonia = dato['neighborhoodId']
                            taller.colonia = dato['neighborhood']
                            taller.codigo_postal = dato['postalCode']
                            taller.id_municipio = dato['cityId']
                            taller.municipio = dato['city']
                            taller.id_estado = dato['stateId']
                            taller.estado = dato['state']
                            taller.telefono = dato['phone']
                            taller.longitud = dato['latitude']
                            taller.latitud = dato['longitude']
                            taller.estatus = 2
                            taller.save()
                            actualizados += 1
                    else:
                        Taller.objects.create(
                            id_empresa=dato['id'],
                            razon_social=dato['name'],
                            direccion=dato['street'],
                            numero_exterior=dato['exteriorNumber'],
                            numero_interior=dato['interiorNumber'],
                            id_colonia=dato['neighborhoodId'],
                            colonia=dato['neighborhood'],
                            codigo_postal=dato['postalCode'],
                            id_municipio=dato['cityId'],
                            municipio=dato['city'],
                            id_estado=dato['stateId'],
                            estado=dato['state'],
                            telefono=dato['phone'],
                            longitud=dato['latitude'],
                            latitud=dato['longitude'],
                            estatus=1
                        )
                        nuevos += 1

            # Recuperar datos que se mostrarán en el frontend
            sin_recepcion = Taller.objects.filter(estatus=3)
            total_sin_recepcion = sin_recepcion.count()
            registros = Taller.objects.all()
            total = registros.count()
            regitro_nuevos = Taller.objects.filter(estatus=1)

            talleres = [
                {'razon_social': t.razon_social, 'estatus': t.estatus_nombre}
                for t in regitro_nuevos
            ]

            context["talleres"] = list(talleres)
            context["leidos"] = leidos
            context["actualizados"] = actualizados
            context["nuevos"] = nuevos
            context["sin_modificacion"] = sin_modificacion
            context["total_sin_recepcion"] = total_sin_recepcion
            context["total"] = total


        else:
            return JsonResponse({"error": f"Error {response.status_code}: {response.text}"}, status=response.status_code)

        return JsonResponse(context)
                
@require_POST
@csrf_exempt
def llantas(request):
    if request.method == "POST":

        pagina = request.POST.get("pagina", 0)

        url = "https://llantas.automatizia.com/apiv2/bots/tires" + "&" + "perPage=100" 
        headers = { "Authorization": settings.TOKEN_BOT }
        response = requests.get(url, headers=headers)

        context = {
            "llantas": [],
        } 

        data = response.json()

#        total_registros = (data['data']['total'])
#        pagina = (data['data']['page'])
#        total_por_pagina = (data['data']['perPage'])
        paginas_totales = int(data['data']['numPages'])

        leidos = 0
        actualizados = 0
        nuevos = 0
        sin_modificacion = 0

        registro_por_pagina = 10

        if int(pagina) == 0:
            inicio = 1
        else:
            inicio = (int(pagina) * registro_por_pagina ) + 1
            if inicio > paginas_totales:
                inicio = paginas_totales

        termina = inicio + registro_por_pagina

        if termina > paginas_totales:
            termina = paginas_totales

        # Borra todos los registros
        InventarioPaso.objects.all().delete()

        # Reinicia el autoincremento del ID en MySQL
        with connection.cursor() as cursor:
            cursor.execute("ALTER TABLE InventarioPaso AUTO_INCREMENT = 1;")

        for i in range(1, paginas_totales):

            url = "https://llantas.automatizia.com/apiv2/bots/tires" + "&" + "page=" + str(i) + "&" + "perPage=100" 
            headers = { "Authorization": settings.TOKEN_BOT }
            response = requests.get(url, headers=headers)


            if response.status_code == 200:

                data = response.json()  # Usa directamente .json()

                for dato in data['data']['rows']:
                    leidos += 1
                    InventarioPaso.objects.create(
                        id_inventario = dato['id'],
                        id_empresa = dato['botId'],
                        producto_clave = dato['sku'],
                        descripcion = dato['name'],
                        ancho = float(dato['width']),
                        alto = float(dato['height']),
                        rin = float(dato['diameter']),
                        existencia = int(dato['stock']),
                        precio = float(dato['price']),
                        estatus=1
                    )
                    leidos += 1


        registros_nuevos = Inventario.objects.filter(estatus=1)
        registros_sin_recepcion = Inventario.objects.filter(estatus=3)
        registros_totales = Inventario.objects.all()
        sin_recepcion = registros_sin_recepcion.count()
        total = registros_totales.count()

        llantas = [
            {'razon_social': t.talleres.razon_social, 'llanta': t.descripcion, 'estatus': t.estatus_nombre}
            for t in registros_nuevos
        ]

        context["llantas"] = list(llantas)
        context["leidos"] = leidos
        context["actualizados"] = actualizados
        context["nuevos"] = nuevos
        context["sin_modificacion"] = sin_modificacion
        context["sin_recepcion"] = sin_recepcion
        context["total"] = total
    else:

        return JsonResponse({"error": f"Error {response.status_code}: {response.text}"}, status=response.status_code)

    return JsonResponse(context)

'''

        inventario = InventarioPaso.objects.all()

        Inventario.objects.all().update(estatus=3)

        for registro in inventario:
            llanta = Inventario.objects.filter(id_inventario=registro.id_inventario).first()
            if registro.id_empresa:
                taller = Taller.objects.filter(id_empresa=registro.id_empresa).first()
                if taller:
                    id_taller = taller.id
            if llanta:
                if (
                    llanta.id_inventario == registro.id_inventario and
                    llanta.id_empresa == registro.id_empresa and
                    llanta.producto_clave == registro.producto_clave and
                    llanta.descripcion == registro.descripcion and
                    llanta.ancho == registro.ancho and
                    llanta.alto == registro.alto and
                    llanta.rin == registro.rin and
                    llanta.existencia == registro.existencia and
                    llanta.precio == registro.precio
                    ):
                    llanta.estatus = 0
                    llanta.save()
                    sin_modificacion += 1
                else:
                    llanta.id_inventario = registro.id_inventario
                    llanta.id_empresa = registro.id_empresa
                    llanta.talleres_id = id_taller
                    llanta.producto_clave = registro.producto_clave
                    llanta.descripcion = registro.descripcion
                    llanta.ancho = registro.ancho
                    llanta.alto = registro.alto
                    llanta.rin = registro.alto
                    llanta.existencia = registro.existencia
                    llanta.precio = registro.precio
                    llanta.estatus = 2
                    llanta.save()
                    actualizados += 1
            else:
                Inventario.objects.create(
                    id_inventario = registro.id_inventario,
                    id_empresa = registro.id_empresa,
                    talleres_id = id_taller,
                    producto_clave = registro.id_empresa,
                    descripcion = registro.descripcion,
                    ancho = registro.ancho,
                    alto = registro.alto,
                    rin = registro.rin,
                    existencia = registro.existencia,
                    precio = registro.precio,
                    estatus=1
                )
                nuevos += 1

        # Recuperar datos que se mostrarán en el frontend
        registros_nuevos = Inventario.objects.filter(estatus=1)
        registros_sin_recepcion = Inventario.objects.filter(estatus=3)
        registros_totales = Inventario.objects.all()
        sin_recepcion = registros_sin_recepcion.count()
        total = registros_totales.count()

        llantas = [
            {'razon_social': t.talleres.razon_social, 'llanta': t.descripcion, 'estatus': t.estatus_nombre}
            for t in registros_nuevos
        ]

        context["llantas"] = list(llantas)
        context["leidos"] = leidos
        context["actualizados"] = actualizados
        context["nuevos"] = nuevos
        context["sin_modificacion"] = sin_modificacion
        context["sin_recepcion"] = sin_recepcion
        context["total"] = total
    else:

        return JsonResponse({"error": f"Error {response.status_code}: {response.text}"}, status=response.status_code)

    return JsonResponse(context)
'''