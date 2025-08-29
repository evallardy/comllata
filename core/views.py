from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
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
from django.contrib.auth.hashers import make_password, check_password
import random
import string
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Min, Max
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from almacen.models import *
from .models import *
from .forms import AvisoForm

# Create your views here.

class AvisoListView(ListView):
    model = Aviso
    template_name = 'core/adminis/avisos/aviso_list.html'
    context_object_name = 'avisos'

class AvisoCreateView(CreateView):
    model = Aviso
    form_class = AvisoForm
    template_name = 'core/adminis/avisos/aviso_form.html'
    success_url = reverse_lazy('aviso_list')

class AvisoUpdateView(UpdateView):
    model = Aviso
    form_class = AvisoForm
    template_name = 'core/adminis/avisos/aviso_form.html'
    success_url = reverse_lazy('aviso_list')

class AvisoDeleteView(DeleteView):
    model = Aviso
    template_name = 'core/adminis/avisos/aviso_confirm_delete.html'
    success_url = reverse_lazy('aviso_list')

def generar_codigo():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=8))

def encrypta_codigo(codigo):
    return make_password(codigo)

def valida_codigo(codigo, cadena):
    if check_password(codigo, cadena):
        print("✅ Código válido")
        return True
    else:
        print("❌ Código inválido")
        return False

def agrega_carrito(request, pk):
    carrito = request.session.get('carrito', {})
    llanta = get_object_or_404(Inventario, pk=pk)

    cantidad = carrito.get(pk, {}).get('cantidad', 0) + 1

    precio_s_iva = float(round(llanta.precio / (1 + settings.IMPUESTO_IVA), 2))
    total_s_iva = float(cantidad) * float(precio_s_iva)
    total = float(cantidad) * float(llanta.precio)
    iva = total - total_s_iva

    carrito[str(pk)] = {
        'id_taller': llanta.empresa.id,
        'razon_social': llanta.empresa.razon_social,
        'descripcion': llanta.descripcion,
        'producto_clave': llanta.producto_clave,
        'cantidad': int(cantidad),
        'precio': float(llanta.precio),
        'precio_s_iva': float(precio_s_iva),
        'iva': iva,
        'total_s_iva': total_s_iva,
        'total': total,
    }

    # Filtrar solo las claves que sean productos (números como string)
    productos = [item for key, item in carrito.items() if key.isdigit()]

    # Recalcular totales
    carrito["piezas"] = sum(item['cantidad'] for item in productos)
    carrito["subtotal"] = round(sum(item['total_s_iva'] for item in productos), 2)
    carrito["iva_total"] = round(sum(item['iva'] for item in productos), 2)
    carrito["total_general"] = round(sum(item['total'] for item in productos), 2)
    carrito["descuento"] = 0

    request.session['carrito'] = carrito

#    adicionales = {
#        'piezas': carrito["piezas"],
#        'subtotal': carrito["subtotal"],
#        'iva_total': carrito["iva_total"],
#        'total_general': carrito["total_general"],
#        'descuento': carrito["descuento"],
#    }

    return JsonResponse({'piezas': carrito["piezas"],
        "message": "Tu petición se registró correctamente"
    }, status=200)

def agrega_carrito_cantidad(request, pk, cantidad):
    carrito = request.session.get('carrito', {})
    llanta = get_object_or_404(Inventario, pk=pk)

    precio_s_iva = float(round(llanta.precio / (1 + settings.IMPUESTO_IVA), 2))
    total_s_iva = float(cantidad) * float(precio_s_iva)
    total = float(cantidad) * float(llanta.precio)
    iva = total - total_s_iva

    carrito[str(pk)] = {
        'id_taller': llanta.empresa.id,
        'razon_social': llanta.empresa.razon_social,
        'descripcion': llanta.descripcion,
        'producto_clave': llanta.producto_clave,
        'cantidad': int(cantidad),
        'precio': float(llanta.precio),
        'precio_s_iva': float(precio_s_iva),
        'iva': iva,
        'total_s_iva': total_s_iva,
        'total': total,
    }

    productos = [item for key, item in carrito.items() if key.isdigit()]

    # Recalcular totales
    carrito["piezas"] = sum(item['cantidad'] for item in productos)
    carrito["subtotal"] = round(sum(item['total_s_iva'] for item in productos), 2)
    carrito["iva_total"] = round(sum(item['iva'] for item in productos), 2)
    carrito["total_general"] = round(sum(item['total'] for item in productos), 2)
    carrito["descuento"] = 0



    request.session['carrito'] = carrito

#    adicionales = {
#        'piezas': carrito["piezas"],
#        'subtotal': carrito["subtotal"],
#        'iva_total': carrito["iva_total"],
#        'total_general': carrito["total_general"],
#        'descuento': carrito["descuento"],
#    }

    producto = carrito[str(pk)] 

    return JsonResponse({
        "producto": producto,
        "piezas": carrito["piezas"],
        "subtotal": carrito["subtotal"],
        "iva_total": carrito["iva_total"],
        "total_general": carrito["total_general"],
        "descuento": carrito["descuento"]
    }, status=200)

@csrf_exempt  # Si usas CSRF token en fetch, puedes omitirlo
def eliminar_del_carrito(request, pk):
    carrito = request.session.get('carrito', {})
    pk = str(pk)

    if pk in carrito:
        del carrito[pk]

    # Recalcular totales
    productos = [item for key, item in carrito.items() if key.isdigit()]
    carrito["piezas"] = sum(item['cantidad'] for item in productos)
    carrito["subtotal"] = round(sum(item['total_s_iva'] for item in productos), 2)
    carrito["iva_total"] = round(sum(item['iva'] for item in productos), 2)
    carrito["total_general"] = round(sum(item['total'] for item in productos), 2)
    carrito["descuento"] = 0

    request.session['carrito'] = carrito
    request.session.modified = True

    return JsonResponse({
        "message": "Producto eliminado del carrito",
        "piezas": carrito["piezas"],
        "subtotal": carrito["subtotal"],
        "iva_total": carrito["iva_total"],
        "total_general": carrito["total_general"],
        "descuento": carrito["descuento"]
    }, status=200)

@csrf_exempt
def vaciar_carrito(request):
    # Obtener carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Eliminar solo los productos (claves numéricas)
    productos = [key for key in carrito if key.isdigit()]
    for key in productos:
        del carrito[key]

    # Reiniciar totales
    carrito["piezas"] = 0
    carrito["subtotal"] = 0
    carrito["iva_total"] = 0
    carrito["total_general"] = 0
    carrito["descuento"] = 0

    request.session['carrito'] = carrito
    request.session.modified = True

    return JsonResponse({
        "message": "Carrito vaciado",
        "piezas": carrito["piezas"],
        "subtotal": carrito["subtotal"],
        "iva_total": carrito["iva_total"],
        "total_general": carrito["total_general"],
        "descuento": carrito["descuento"]
    }, status=200)

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

    return render(request, 'core/cliente/home.html', { 'context': context })
class BaseClienteView(TemplateView):
    mensaje_cliente = "Mensajes para el cliente"
    producto = Inventario.objects.all().first()
    producto_mas_vendido = producto.descripcion
    producto_mas_vendido_id = producto.id
    producto_precios = Inventario.objects.filter(id=producto_mas_vendido_id) \
    .aggregate(
        precio_minimo=Min('precio'),
        precio_maximo=Max('precio')
    )
    precio_maximo = producto_precios['precio_maximo'] or 0
    precio_minimo = producto_precios['precio_minimo'] or 0
    alto = 0
    ancho = 0
    rin = 0
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = self.request.session.get('carrito', {})

        if len(carrito) == 0:
            adicionales = {
                'piezas': 0,
                'subtotal': 0,
                'iva_total': 0,
                'total_general': 0,
                'descuento': 0,
            }
            carrito["piezas"] = 0
        else:
            adicionales = {
                'piezas': carrito["piezas"],
                'subtotal': carrito["subtotal"],
                'iva_total': carrito["iva_total"],
                'total_general': carrito["total_general"],
                'descuento': carrito["descuento"],
            }


        context = super().get_context_data(**kwargs)
        context["mensaje_cliente"] = self.mensaje_cliente
        context["anio_actual"] = '2025'
        context["producto_mas_vendido"] = self.producto_mas_vendido
        context["precio_maximo"] = self.precio_maximo
        context["precio_minimo"] = self.precio_maximo
        context['adicionales'] = adicionales
        context['piezas'] = carrito["piezas"]

        return context

class MuestraTaller(BaseClienteView, TemplateView):
    template_name = 'core/diseno/NiceShop/ubica-taller.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener pk desde kwargs
        pk = self.kwargs.get('pk')

        # Obtener taller o 404
        taller = get_object_or_404(Taller, pk=pk)

        latitud = taller.latitud
        longitud = taller.longitud

        if latitud and longitud:

            ubicacion = f"https://www.google.com/maps/embed/v1/view?key=TU_API_KEY&center={latitud},{longitud}&zoom=16&maptype=roadmap"
        else:
            ubicacion = 'https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d48389.78314118045!2d-74.006138!3d40.710059!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c25a22a3bda30d%3A0xb89d1fe6bc499443!2sDowntown%20Conference%20Center!5e0!3m2!1sen!2sus!4v1676961268712!5m2!1sen!2sus'

        context['taller'] = taller
        context['ubicacion'] = ubicacion

        return context

class Carrito(BaseClienteView, TemplateView):
    template_name = 'core/diseno/NiceShop/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class About(BaseClienteView, TemplateView):
    model = Aviso
    template_name = 'core/diseno/NiceShop/about.html'
    context_object_name = 'avisos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class Contact(BaseClienteView, TemplateView):
    model = Aviso
    template_name = 'core/diseno/NiceShop/contact.html'
    context_object_name = 'avisos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class MuestraProductosTaller(BaseClienteView, TemplateView):
    template_name = 'core/diseno/NiceShop/muestra-productos-taller.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        medidas = self.request.session.get('medidas')
        alto = medidas['alto']
        ancho = medidas['ancho']
        rin = medidas['rin']

        inventario = Inventario.objects.filter(empresa_id=pk, alto=alto, ancho=ancho, rin=rin, existencia__gt=0).order_by('precio')

        taller = get_object_or_404(Taller, id_empresa=pk)

        context['inventario'] = inventario
        context['taller'] = taller

        return context
    
class MuestraProductos(BaseClienteView, TemplateView):
    template_name = 'core/diseno/NiceShop/muestra-productos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Intentar obtener el usuario a actualizar
        comentario = ""

        busqueda_llantas = ""

        inventario_por_taller = ''

        texto = request.POST.get('q', '') + " "

        if settings.ACTIVA_IA:

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

        else:
    
            datos = {
                "marca": "Audi",
                "modelo": "A3",
                "año": "2016",
                "ancho": 225,
                "alto": 45,
                "rin": 17
            }

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
            texto1 += 'La llanta a buscar es de un auto '
            texto1 += f'Marca {marca} , '
            texto1 += f'Modelo {modelo}, '
            texto1 += f'Año {anio} '
        if alto and ancho and rin:
            if marca and modelo and anio:
                texto1 += ', y ocupa una llanta con medidas '
            else:
                texto1 += 'Las medidas que me solicitas son '
            texto1 += f'Alto {alto}, '
            texto1 += f'Ancho {ancho}, '
            texto1 += f'Rin {rin} '

            self.alto = alto
            self.ancho = ancho
            self.rin = rin

        presenta = False
        empresas_dict = {}

        if medida1 and medida2 and medida3:
            llantas1 = Inventario.objects.filter(empresa__isnull=True, estatus=1)

            llantas = Inventario.objects.filter(ancho=ancho, alto=alto, rin=rin, existencia__gt=0).order_by('empresa', 'precio')

            # Agrupar por taller
            for inv in llantas:
                key = str(inv.empresa.id)  # ID como clave
                if key not in empresas_dict:
                    empresas_dict[key] = {
                        "id": inv.empresa.id,
                        "llave": inv.empresa.id_empresa,
                        "razon_social": inv.empresa.razon_social,
                        "productos": []
                    }
                empresas_dict[key]["productos"].append({
                    "id": inv.id,
                    "descripcion": inv.descripcion,
                    "precio": float(inv.precio),
                    "existencia": inv.existencia
                })
            cantidad = llantas.count()
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
        
        request.session['empresas_dict'] = empresas_dict
        request.session['detalle_llanta'] = texto1
        request.session['medidas'] = {'alto':alto, 'ancho':ancho, 'rin':rin}

        return render(request, self.template_name, context)

class BuscarLlantaView(BaseClienteView):
    
    template_name = "core/diseno/NiceShop/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["procesado"] = False  # Para saber si ya se ejecutó
        avisos = Aviso.objects.all()
        context["avisos"] = [aviso for aviso in avisos if aviso.is_activo]
        return context

    def post(self, request, *args, **kwargs):

        comentario = ""

        busqueda_llantas = ""

        inventario_por_taller = ''

        texto = request.POST.get('q', '') + " "

        if settings.ACTIVA_IA:

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

        else:
    
            datos = {
                "marca": "Audi",
                "modelo": "A3",
                "año": "2016",
                "ancho": 225,
                "alto": 45,
                "rin": 17
            }

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
            llantas1 = Inventario.objects.filter(empresa__isnull=True, estatus=1)

            llantas = Inventario.objects.filter(ancho=ancho, alto=alto, rin=rin, existencia__gt=0).order_by('empresa', 'precio')

            # Agrupar por taller
            inventario_por_taller = defaultdict(list)
            for item in llantas:
                if item.empresa:  # Evitar talleres nulos
                    inventario_por_taller[item.empresa].append(item)

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
    mensaje_administracion = "Javier camarillo Noemi"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mensaje_administracion"] = self.mensaje_administracion
        context["anio_actual"] = '2025'
        return context

class AdministracionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/adminis/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["procesado"] = False
        return context
    
@method_decorator(staff_member_required(login_url='/administracion/'), name='dispatch')
class ImportacionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/adminis/importar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context    
    
class ActualizacionView(BaseAdministracionMixin, TemplateView):
    template_name = "core/adminis/actualiza.html"

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