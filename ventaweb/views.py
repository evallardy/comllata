from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import VentaPaypal
import json
from django.utils.decorators import method_decorator

from almacen.models import *
from ventaweb.models import *

# python manage.py runsslserver --certificate localhost.pem --key localhost-key.pem

@method_decorator(csrf_exempt, name='dispatch')
class RegistrarVentaPaypalView(View):
    def post(self, request):
        usuario = request.user if request.user.is_authenticated else None

        try:
            datos = json.loads(request.body)

            total_calculado = 0
            carrito = datos.get('carrito', {})
            detalles = []

            # Validar y calcular el total desde la base de datos
            for producto_id, item in carrito.items():
                cantidad = int(item.get('cantidad', 0))
                precio = float(item.get('precio', 0))
                descripcion = item.get('descripcion', '')
                id_inventario = item.get('inventario', '')
                id_empresa = item.get('empresa', '')

                inventario = Inventario.objects.filter(id_inventario=id_inventario).first()

                if not inventario:
                    return JsonResponse({'status': 'error', 'error': f'Producto {id_inventario} no encontrado del taller {id_empresa}'})

                # Validar que el precio coincida
                if float(inventario.precio) != precio:
                    return JsonResponse({'status': 'error', 'error': f'Precio no válido para {descripcion} del taller {id_empresa}'})

                importe = cantidad * precio
                total_calculado += importe

                detalles.append({
                    'id_inventario': id_inventario,
                    'id_empresa': id_empresa,
                    'descripcion': descripcion,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'importe': importe
                })

            total_enviado = datos.get('total', 0)

            # Validar total enviado vs calculado
            if round(total_calculado, 2) != round(float(total_enviado), 2):
                return JsonResponse({'status': 'error', 'error': f'Total {total_enviado} no coincide con el calculado {total_calculado}, {cantidad}, {precio}'})

            venta = VentaPaypal.objects.create(
                paypal_order_id = datos['order_id'],
                nombre_cliente = datos['nombre'],
                email_cliente = datos['email'],
                nombre_completo = datos.get('nombre_completo', ''),
                direccion = datos.get('direccion', ''),
                ciudad = datos.get('ciudad', ''),
                estado = datos.get('estado', ''),
                cp = datos.get('cp', ''),
                pais = datos.get('pais', ''),
                fecha_creacion = datos['fecha_creacion'],
                total = round(total_calculado, 2),
                comprador=request.user if request.user.is_authenticated else None
            )

            for d in detalles:
                VentaDetalle.objects.create(
                    venta=venta,
                    id_inventario=d['id_inventario'],
                    id_empresa=d['id_empresa'],
                    descripcion=d['descripcion'],
                    cantidad=d['cantidad'],
                    precio_unitario=d['precio_unitario'],
                    importe=d['importe'],
                    usuario=usuario
                )

            return JsonResponse({'status': 'ok', 'venta_id': venta.id})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})

class Venta(ListView):
    template_name = 'ventaweb/venta.html'
    context_object_name = 'productos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        alto_distintos = Inventario.objects.values_list('alto', flat=True).distinct().order_by('alto')
        ancho_distintos = Inventario.objects.values_list('ancho', flat=True).distinct().order_by('ancho')
        rin_distintos = Inventario.objects.values_list('rin', flat=True).distinct().order_by('rin')

        context['alto_distintos']=alto_distintos
        context['ancho_distintos']=ancho_distintos
        context['rin_distintos']=rin_distintos

        context['maxima_seleccion']=0
        context['seleccion_alto']=0
        context['seleccion_ancho']=0
        context['seleccion_rin']=0

        context['cantidad_productos']=Inventario.objects.all().count()

        return context

    def get_queryset(self):
        return Inventario.objects.all().order_by('alto','ancho','rin')[:100]

def filtrar_combos(request):
    """Vista para filtrar opciones dinámicamente y devolver JSON"""
    campo1 = request.GET.get('campo1', '')
    campo2 = request.GET.get('campo2', '')
    campo3 = request.GET.get('campo3', '')
    campo11 = request.GET.get('campo11', '')
    campo22 = request.GET.get('campo22', '')
    campo33 = request.GET.get('campo33', '')

    if campo1=='ancho':
        ancho = campo11
        seleccion_ancho = 1
    elif campo1=='alto':
        alto = campo11
        seleccion_alto = 1
    elif campo1=='rin':
        rin = campo11
        seleccion_rin = 1

    if campo2=='ancho':
        ancho = campo22
        seleccion_ancho = 2
    elif campo2=='alto':
        alto = campo22
        seleccion_alto = 2
    elif campo2=='rin':
        rin = campo22
        seleccion_rin = 2

    if campo3=='ancho':
        ancho = campo33
        seleccion_ancho = 3
    elif campo3=='alto':
        alto = campo33
        seleccion_alto = 3
    elif campo3=='rin':
        rin = campo33
        seleccion_rin = 3

    # Inicializar filtros
    detalle_alto = Q()
    detalle_ancho = Q()
    detalle_rin = Q()

    if campo3 != "":
        if campo3 == 'ancho' and campo2 == 'alto' and campo1 == 'rin':
            detalle_ancho &= Q(alto=alto)
            detalle_ancho &= Q(rin=rin)
            detalle_alto &= Q(rin=rin)
        if campo3 == 'ancho' and campo2 == 'rin' and campo1 == 'alto':
            detalle_ancho &= Q(rin=rin)
            detalle_ancho &= Q(alto=alto)
            detalle_rin &= Q(alto=alto)
        if campo3 == 'rin' and campo2 == 'alto' and campo1 == 'ancho':
            detalle_rin &= Q(alto=alto)
            detalle_rin &= Q(ancho=ancho)
            detalle_alto &= Q(ancho=ancho)
        if campo3 == 'rin' and campo2 == 'ancho' and campo1 == 'alto':
            detalle_rin &= Q(ancho=ancho)
            detalle_rin &= Q(alto=alto)
            detalle_ancho &= Q(alto=alto)
        if campo3 == 'alto' and campo2 == 'ancho' and campo1 == 'rin':
            detalle_alto &= Q(ancho=ancho)
            detalle_alto &= Q(rin=rin)
            detalle_ancho &= Q(rin=rin)
        if campo3 == 'alto' and campo2 == 'rin' and campo1 == 'ancho':
            detalle_alto &= Q(rin=rin)
            detalle_alto &= Q(ancho=ancho)
            detalle_rin &= Q(ancho=ancho)
    elif campo2 != "":
        if campo2 == 'ancho' and campo1 == 'alto':
            detalle_rin &= Q(ancho=ancho)
            detalle_rin &= Q(alto=alto)
            detalle_ancho &= Q(alto=alto)
        if campo2 == 'ancho' and campo1 == 'rin':
            detalle_alto &= Q(ancho=ancho)
            detalle_alto &= Q(rin=rin)
            detalle_ancho &= Q(rin=rin)
        if campo2 == 'alto' and campo1 == 'ancho':
            detalle_rin &= Q(alto=alto)
            detalle_rin &= Q(ancho=ancho)
            detalle_alto &= Q(ancho=ancho)
        if campo2 == 'alto' and campo1 == 'rin':
            detalle_ancho &= Q(alto=alto)
            detalle_ancho &= Q(rin=rin)
            detalle_alto &= Q(rin=rin)
        if campo2 == 'rin' and campo1 == 'alto':
            detalle_ancho &= Q(rin=rin)
            detalle_ancho &= Q(alto=alto)
            detalle_rin &= Q(alto=alto)
        if campo2 == 'rin' and campo1 == 'ancho':
            detalle_alto &= Q(rin=rin)
            detalle_alto &= Q(ancho=ancho)
            detalle_rin &= Q(ancho=ancho)
    else:
        if campo1 == 'ancho':
            detalle_alto &= Q(ancho=ancho)
            detalle_rin &= Q(ancho)
        if campo1 == 'alto':
            detalle_rin &= Q(alto=alto)
            detalle_ancho &= Q(alto=alto)
        if campo1 == 'rin':
            detalle_alto &= Q(rin=rin)
            detalle_ancho &= Q(rin=rin)
            
    # Aplicar filtros a combos
    productos_filtrados_alto = Inventario.objects.filter(detalle_alto)
    productos_filtrados_ancho = Inventario.objects.filter(detalle_ancho)
    productos_filtrados_rin = Inventario.objects.filter(detalle_rin)

    # Obtener valores únicos
    altos = productos_filtrados_alto.values_list('alto', flat=True).distinct().order_by('alto')
    anchos = productos_filtrados_ancho.values_list('ancho', flat=True).distinct().order_by('ancho')
    rines = productos_filtrados_rin.values_list('rin', flat=True).distinct().order_by('rin')

    return JsonResponse({
        'altos': list(altos),
        'anchos': list(anchos),
        'rines': list(rines),
    })

def filtrar_llantas(request):
    filtro = Q()

    campo1 = request.GET.get('campo1', '')
    campo2 = request.GET.get('campo2', '')
    campo3 = request.GET.get('campo3', '')
    campo11 = request.GET.get('campo11', '')
    campo22 = request.GET.get('campo22', '')
    campo33 = request.GET.get('campo33', '')

    if campo1:
        filtro &= Q(campo1=campo11)
    if campo2:
        filtro &= Q(campo2=campo22)
    if campo3:
        filtro &= Q(campo3=campo33)

    # Aplicar filtros a combos
    productos_filtrados = Inventario.objects.filter(filtro)
    # Serializar los datos en JSON
    productos_json = [
        {
            "id": p.id,
            "alto": p.alto,
            "ancho": p.ancho,
            "rin": p.rin,
            "descripcion": p.descripcion,
            "precio": "{:,.2f}".format(p.precio),  # Formato de miles con coma y dos decimales
            "existencia": "{:,.0f}".format(p.existencia),  # Formato de miles con coma y dos decimales
#            "imagen_principal": p.imagen_principal.name
        }
        for p in productos_filtrados
    ]
    html = render_to_string("ventaweb/_card.html", {"producto": productos_json})  # para un solo producto

    tarjetas = [render_to_string("ventaweb/_card.html", {"producto": p}, request=request) for p in productos_json]

    return JsonResponse({
        "html_tarjetas": tarjetas,
        'productos_filtrados': productos_json,
        'cantidad_productos': productos_filtrados.count(),
    })

class VentaDetalleListView(ListView):
    model = VentaDetalle
    template_name = 'ventaweb/pedidos.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        id_empresa = self.request.user.taller.id_empresa
        return VentaDetalle.objects.filter(estatus=0, id_empresa=id_empresa).select_related('venta').order_by('venta_id')

class SurtirVentaView(View):
    def post(self, request, venta_id):
        ahora = timezone.now()
        VentaDetalle.objects.filter(venta_id=venta_id).update(estatus=1, fecha_entrega=ahora)
        return redirect('lista_ventas')
    
class EntregaDetalleListView(ListView):
    model = VentaDetalle
    template_name = 'ventaweb/entregas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        id_empresa = self.request.user.taller.id_empresa
        return VentaDetalle.objects.filter(estatus=1, id_empresa=id_empresa).select_related('venta').order_by('-fecha_entrega')
