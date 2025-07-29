from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from datetime import date
from django.views.generic import TemplateView
from django.http import JsonResponse
import re
import sys
import google.generativeai as genai
import json
from collections import defaultdict

from almacen.models import *
from .models import *

# Create your views here.

def home(request):

    llantas = Llanta.objects.all()
    vehiculos = Vehiculo.objects.exclude(nombre='Auto').filter(estatus=True)

    hoy = date.today()
    avisos = Aviso.objects.filter(
        fecha_inicial__lte=hoy,
        fecha_final__gte=hoy
    ).first()
    if avisos:
        aviso = avisos.aviso
        aviso_template = render_to_string("core/_aviso.html", {"aviso": aviso})  
    else:
        aviso_template = ''

    anchos = Llanta.objects.values_list('ancho', flat=True).distinct().order_by('ancho')
    menu_anchos = [
        {
            "descripcion": f"ancho {ancho}",
            "imagen": f"core/img/ancho/a{ancho}.png"
        }
        for ancho in anchos if ancho
    ]
    menu_ancho_template = render_to_string("core/_muestra_rines.html", {"menu_anchos": menu_anchos})  

    altos = Llanta.objects.values_list('alto', flat=True).distinct().order_by('alto')
    menu_alto = [
        {
            "descripcion": f"alto {alto}",
            "imagen": f"core/img/rin/a{alto}.png"
        }
        for alto in altos if alto
    ]
    menu_alto_template = render_to_string("core/_muestra_rines.html", {"menu_alto": menu_alto})  

    rines = Llanta.objects.values_list('rin', flat=True).distinct().order_by('rin')
    menu_rines = [
        {
            "descripcion": f"Rin {rin}",
            "imagen": f"core/img/rin/r{rin}.png"
        }
        for rin in rines if rin
    ]

#    menu_rines = MenuOpciones.objects.filter(menus__menu='menu_rines', menus__estatus=True, estatus=True)
    menu_rines_template = render_to_string("core/_muestra_rines.html", {"menu_rines": menu_rines})  

    context = {
        'llantas': llantas,
        'aviso_template': aviso_template,
        'vehiculos': vehiculos,
        'menu_ancho_template': menu_ancho_template,
        'menu_alto_template': menu_alto_template,
        'menu_rines_template': menu_rines_template,
    } 

    return render(request, 'core/home_cliente.html', { 'context': context })



class BaseClienteView(TemplateView):
    mensaje_cliente = "Mensajes para el cliente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mensaje_cliente"] = self.mensaje_cliente
        context["anio_actual"] = '2025'
        return context

class BuscarLlantaView(BaseClienteView):
    template_name = "core/home_cliente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["procesado"] = False  # Para saber si ya se ejecutó
        return context

    def post(self, request, *args, **kwargs):

        comentario = ""

        busqueda_llantas = ""

        inventario_por_taller = ''

        texto = request.POST.get('q', '') + " "

        genai.configure(api_key=settings.APIKEY_GOOGLE)
        sys.stdout.reconfigure(encoding='utf-8')
        modeloIA = genai.GenerativeModel('gemini-2.0-flash')
        pregunta = "que llanta en ancho, alto y rin ocupa el '" + texto + " ' , solo entregame la informacion en formato json , de el ancho,  el alto y rin solo los +" \
            "numeros sin unidad de medida, que sean valores estandar, ademas en el json , ponme la marca el modelo y año del auto que tomaste la información, " + \
            " si no encuentra informacion para el auto, solo enviame un resume en un mensaje para avisar en una variable llamada comentario dentro del json json"
        json_string = modeloIA.generate_content(pregunta)
        if not json_string:
            pregunta = "en el siguiente texto nos envian las medidas de una llanta, dime cuales son " + \
                       "' entregame la respuesta en formato json, solo entregame el ancho, el alto y el rin, estos valores son numericos, adicionalmente remplaza en el texto de entrada las diagonales por espacios " + \
                       " antes de procesar, si tienes algun cometnario de esto, enviamelo en la variable comentario, no me entregues mas información, solo la que te pido " + \
                       ", el texto es el siguiente " + texto
            json_string = modeloIA.generate_content(pregunta)
        json_string = json_string.text
        limpio = json_string.strip("`").strip("json").strip()
        clean_json = limpio.replace('\n', '')

        match = re.search(r'\[\s*.*?\s*\]', clean_json, re.DOTALL)

        if match:
            respuesta = match
        else:
            respuesta = json_string

        # Elimina las marcas ```json y ```
        limpio_json = limpio.replace("```json", "").replace("```", "").strip()

        # Convierte a objeto Python
        datos = json.loads(limpio_json)

#        datos = {
#            "marca": "Ford",
#            "modelo": "Mustang",
#            "año": "2015",
#            "ancho": 235,
#            "alto": 55,
#            "rin": 17
#        }

        opcion_seleccionada = []
        opcion_seleccionada.append(datos)

        medida1 = medida2 = medida3 = False
        marca = modelo = anio = ancho = alto = rin = texto1 = ''
        cantidad = 0

        if not comentario:
            for columna, dato in datos.items():
                if not isinstance(dato, str):
                    valor = str(dato)
                else:
                    valor = dato
                if 'ancho' == columna and dato:
                    medida1 = True
                    ancho = dato
                if 'alto' == columna and dato:
                    medida2 = True
                    alto = dato
                if 'rin' == columna and dato:
                    medida3 = True
                    rin = dato
                if 'marca' == columna and dato:
                    marca = dato
                if 'modelo' == columna and dato:
                    modelo = dato
                if 'año' == columna and dato:
                    anio = dato
                if 'comentario' == columna and dato:
                    comentario = dato

        mensaje = ''
        try:
            ancho = int(ancho)
        except (TypeError, ValueError):
            ancho = 0

        try:
            alto = int(alto)
        except (TypeError, ValueError):
            alto = 0

        try:
            rin = int(rin)
        except (TypeError, ValueError):
            rin = 0
            
        if marca and modelo and anio:
            texto1 += 'El primer auto que encontré con la especificación que me das es el siguiente :<br>'
            texto1 += f'   Marca  : {marca}<br>'
            texto1 += f'   Modelo : {modelo}<br>'
            texto1 += f'   Año    : {anio}<br>'
        if alto and ancho and rin:
            if marca and modelo and anio:
                texto1 += 'Este auto ocupa una llanta con las siguientes medidas : <br>'
            else:
                texto1 += 'Las medidas que me solicitas son las siguientes : <br>'
            texto1 += f'   Alto   : {alto}<br>'
            texto1 += f'   Ancho  : {ancho}<br>'
            texto1 += f'   Rin    : {rin}<br>'
            texto1 += '<br>A continuación te muestro las opciones que tengo.'

        presenta = False

        if medida1 and medida2 and medida3:
            llantas1 = InventarioPaso.objects.filter(talleres__isnull=True, estatus=1)

            for llanta in llantas1:
                taller = Taller.objects.filter(id_empresa=llanta.id_empresa).first()
                llanta.estatus = 0
                if taller and llanta.talleres != taller:
                    llanta.talleres = taller
                llanta.save()

            llantas = InventarioPaso.objects.filter(ancho=ancho, alto=alto, rin=rin).order_by('talleres', 'precio')

            # Agrupar por taller
            inventario_por_taller = defaultdict(list)
            for item in llantas:
                if item.talleres:  # Evitar talleres nulos
                    inventario_por_taller[item.talleres].append(item)

            context = {
                'ancho': ancho,
                'alto': alto,
                'rin': rin,
                'inventario_por_taller': dict(inventario_por_taller)
            }


            cantidad = llantas.count()
            busqueda_llantas = render_to_string("core/_presenta_taller.html", context) 
            presenta = True
        else:
            opcion_seleccionada = []
            if comentario:
                datos = {
                    "comentario": comentario,
                }
            else:
                datos = {
                    "comentario": "No entendi lo que me pediste, puedes poner el auto con marca, modelo y año " \
                        " o puedes darme las medidas de la llanta de tu auto",
                }
            opcion_seleccionada.append(datos)
        
        context = {
            'opcion_seleccionada': opcion_seleccionada,
            'busqueda_llantas': busqueda_llantas, 
            'presenta': presenta,
            'cantidad': cantidad,
            'texto1':texto1,
            'inventario_por_taller':inventario_por_taller
        }

        return render(request, self.template_name, {'context': context})
    
class BaseAdministracionMixin:
    mensaje_administracion = "Mensajes para la administración"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mensaje_administracion"] = self.mensaje_administracion
        context["anio_actual"] = '2025'
        return context

class AdministracionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/home_adminis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["procesado"] = False
        return context
    
class ImportacionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/home_adminis_importar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context    
    
class ActualizacionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/home_adminis_actualiza.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["procesado"] = False  # Para saber si ya se ejecutó
        return context
    
def actualiza(request):    
    context = {} 
    total_procesados = 0
    total_actualizados = 0
    total_fallidos = 0

    inventarios = Inventario.objects.filter(producto_clave__isnull=False, actualizado=0)

    for inv in inventarios:
        fallo = False
        clave = inv.producto_clave.strip()
        total_procesados += 1

        ancho = alto = rin = marca_nombre = modelo_raw = None

        # === Formato 1 ===
        match1 = re.search(r'(\d{3})/(\d{2})_R(\d{2})[_\s]+([A-Za-z0-9]+)[_\s]+(.+)', clave)
        if match1:
            ancho = match1.group(1)
            alto = match1.group(2)
            rin = match1.group(3)
            marca_nombre = match1.group(4).strip().upper()
            modelo_raw = match1.group(5).strip().replace('_', ' ').upper()

        else:
            # === Formato 2 ===
            match2 = re.search(r'(\d{3})/(\d{2})R(\d{2})\s+([A-Za-z]+)\s+(.+)', clave)
            if match2:
                ancho = match2.group(1)
                alto = match2.group(2)
                rin = match2.group(3)
                marca_nombre = match2.group(4).strip().upper()
                modelo_raw = match2.group(5).strip().upper()
            else:
                # === Formato 3 ===
                match3 = re.match(r'^(\d{3})(\d{2})(\d{2})([A-Z]+)([A-Z0-9]*)$', clave)
                if match3:
                    ancho = match3.group(1)
                    alto = match3.group(2)
                    rin = match3.group(3)
                    marca_nombre = match3.group(4).strip().upper()
                    modelo_raw = match3.group(5).strip().upper() if match3.group(5) else ''
                else:
                    total_fallidos += 1
                    fallo = True
                    
        if not fallo:

            # Buscar o crear marca y llanta
            marca, _ = MarcaLlanta.objects.get_or_create(
                nombre__iexact=marca_nombre, defaults={"nombre": marca_nombre}
            )
            llanta, _ = Llanta.objects.get_or_create(
                marca=marca,
                modelo=modelo_raw,
                ancho=ancho,
                alto=alto,
                rin=rin
            )

            inv.llantas = llanta 
            inv.actualizado = 1
            inv.save()
            total_actualizados += 1

    context["total_procesados"] = total_procesados
    context["total_actualizados"] = total_actualizados
    context["total_fallidos"] = total_fallidos
    return JsonResponse(context)