import bcrypt
from django.core.mail import send_mail
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
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from core.views import generar_codigo, encrypta_codigo, valida_codigo
from almacen.models import *
from ventaweb.models import *

# python manage.py runsslserver --certificate localhost.pem --key localhost-key.pem

@require_POST
def verificar_codigo_entrega(request):
    venta_id = request.POST.get('venta_id')
    codigo_cliente = request.POST.get('codigo')

    venta = VentaDetalle.objects.filter(id=venta_id).first()

    if venta is None:
        return JsonResponse({'status': 'error', 'mensaje': 'Venta no encontrada'})

    if venta.estatus:
        return JsonResponse({'status': 'error', 'mensaje': f'Esta venta ya fue entregada.'})

    if valida_codigo(codigo_cliente, venta.token_hash):
        venta.estatus = True
        venta.save()
        return JsonResponse({'status': 'ok', 'mensaje': 'Venta entregada correctamente.'})
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'Código incorrecto.'})

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
                descripcion = item.get('descripcion', '')
                cantidad = int(item.get('cantidad', 0))
                precio = float(item.get('precio', 0))
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

            compras = []

            for d in detalles:

                token = generar_codigo()
                token_hash = encrypta_codigo(token)

                venta_detalle = VentaDetalle.objects.create(
                    venta=venta,
                    id_inventario=d['id_inventario'],
                    id_empresa=d['id_empresa'],
                    descripcion=d['descripcion'],
                    cantidad=d['cantidad'],
                    precio_unitario=d['precio_unitario'],
                    importe=d['importe'],
                    usuario=usuario,
                    token_hash=token_hash
                )

                taller = Taller.objects.filter(id_empresa=d['id_empresa']).first()

                razon_social = taller.razon_social.upper()

                compras.append({
                    'id': venta_detalle.id,
                    'descripcion': venta_detalle.descripcion,
                    'cantidad': venta_detalle.cantidad,
                    'token': token,
                    'taller': taller.razon_social,
                })

                if venta_detalle.cantidad == 1:
                    mensaje_llanta = ' tu llanta '
                    mensaje_recoger = ' recoger'
                else:
                    mensaje_llanta = ' tus llantas '
                    mensaje_recoger = ' recogerlas'

                mensaje_html = f'''
                    <div style="font-size: 18px;">La compra de {mensaje_llanta} con medidas:<br><br> 
                    <code>{venta_detalle.descripcion or ""}</code><br><br> 
                    quedó registrada en el taller:<br><br>
                    <code>{razon_social or ""}</code><br><br>
                    Número de venta: <br><br>
                    <code>{venta_detalle.id}</code><br><br>
                    Además presenta este código:<br><br>
                    <code>{token}</code><br><br>
                    Para que pases a {mensaje_recoger} en:<br><br>
                    <code>
                        {taller.direccion or ""}, 
                        {taller.numero_exterior or ""} 
                        {taller.numero_interior or ""} 
                        {taller.colonia or ""}<br>
                        {taller.codigo_postal or ""} 
                        {taller.municipio or ""} 
                        {taller.estado or ""}<br>
                        teléfono {taller.telefono or ""}
                    </code><br><br>
                    NO ES NECESARIO RESPONDER A ESTE CORREO
                    </div>
                '''
                send_mail(
                    subject='Tu pedido ha sido registrado',
                    message='Texto adicional',
                    from_email='evalalrdy@gmail.com',
                    recipient_list=[venta.email_cliente,],
                    html_message=mensaje_html
                )

            return JsonResponse({'status': 'ok', 'compras': compras})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})

def pruebaEnvio(request, venta_id):
    try:
        venta = VentaDetalle.objects.filter(id=venta_id).first()

        if not venta:
            return JsonResponse({'status': 'error', 'mensaje': 'Venta no encontrada'})

        taller = Taller.objects.filter(id_empresa='6c8349cc7260ae62e3b1396831a8398f').first()

        if not taller:
            return JsonResponse({'status': 'error', 'mensaje': 'Taller no encontrado'})

        # Simula un token (o reemplaza con uno real)
        token = 'abc123de'

        razon_social = taller.razon_social.upper()

        mensaje_html = f'''
        <p>Tu venta quedó registrada en el taller <b>{razon_social}</b>,<br>
        con el número <strong>{venta.id}</strong>, para que pases a recogerlo.<br>
        Además presenta este código:</p>
        <p style="font-size: 18px;"><code>{token}</code></p>
        <p>Dirección:<br>
        {taller.direccion}, {taller.numero_exterior} {taller.numero_interior} {taller.colonia}<br>
        {taller.codigo_postal} {taller.municipio} {taller.estado}<br>
        Teléfono: {taller.telefono}<br><br>
        NO ES NECESARIO RESPONDER A ESTE CORREO
        </p>
        '''

        send_mail(
            subject='Tu pedido ha sido registrado',
            message='Texto adicional',
            from_email='evalalrdy@gmail.com',
            recipient_list=['evallardy@gmail.com'],
            html_message=mensaje_html
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

class EnviarConfirmaVentaView(View):
    def get(self, request, *args, **kwargs):
        # Obtener el curso por pk
        curso = get_object_or_404(Curso, pk=kwargs['pk'])

        # Crear el formulario
        form = CorreoForm(initial={
#            'destinatario': curso.empresa.correo,
            'destinatario': curso.empresa.correo,
            'asunto': f'QR para registro del curso {curso.tema.nombre}',
            'contenido': f'Este correo contiene el QR para registro del curso "{curso.tema.nombre}".',
        })

        # Genera el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f'https://descapa.iagmexico.com/core/asistentes/registrar/{curso.pk}/'  # URL del curso
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')

        # Guarda la imagen en un objeto BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Codifica la imagen a base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        img_url = f"data:image/png;base64,{img_base64}"

        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'curso': curso,
            'qr_url': img_url
        })

    def post(self, request, *args, **kwargs):
        # Obtener el curso por pk
        curso = get_object_or_404(Curso, pk=kwargs['pk'])
        
        # Crear el formulario con los datos enviados
        form = CorreoForm(request.POST)

        if form.is_valid():
            # Obtener los datos del formulario
            destinatario = form.cleaned_data['destinatario']
            asunto = form.cleaned_data['asunto']
            contenido = form.cleaned_data['contenido']

            # Generar el código QR nuevamente
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f'https://descapa.iagmexico.com/core/asistentes/registrar/{curso.pk}/'  # URL del curso
#            qr_data = f'//localhost:8000/core/asistentes/registrar/{curso.pk}/'  # URL del curso
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')

            # Guarda la imagen en un objeto BytesIO
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Codifica la imagen a base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            img_url = f"data:image/png;base64,{img_base64}"

            # Preparar el correo
            # from_email = settings.EMAIL_HOST_USER
            from_email = 'soporte@iagmexico.com'
            recipient_list = [destinatario]  # Usar el correo proporcionado por el usuario

            # Crear el mensaje del correo
            email = EmailMessage(
                asunto,  # Asunto
                contenido,  # Contenido
                from_email,  # De quien lo envia
                recipient_list,  # Destinatarios
            )

            # Adjuntar la imagen del QR al correo
            email.attach(
                f"qr_curso_{curso.pk}.png",  # Nombre del archivo
                img_io.getvalue(),  # Imagen en formato binario
                "image/png"  # Tipo de contenido
            )

            # Enviar el correo
            try:
                email.send()
#                messages.success(request, "Correo enviado correctamente.")
                respuesta = 'Correo enviado correctamente'
            except Exception as e:
#                messages.error(request, f"Error al enviar el correo: {str(e)}")
                respuesta = f"Error al enviar el correo: {str(e)}"

            # Redirigir a la página de éxito o mostrar mensaje
            return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
                'form': form,
                'curso': curso,
                'qr_url': img_url,
                'respuesta': respuesta,
            })
        
        # Si el formulario no es válido, volver a mostrar el formulario con errores
        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'curso': curso,
            'qr_url': img_url
        })

def verificar_codigo_entrega2(request):
    if request.method == 'POST':
        venta_id = request.POST.get('venta_id')
        codigo_cliente = request.POST.get('codigo')

        # Buscar la venta sin importar el estatus
        venta = VentaDetalle.objects.filter(id=venta_id).first()

        if not venta:
            return JsonResponse({'status': 'error', 'mensaje': 'No se encontró la venta con ese ID.'})

        if venta.estatus:
            return JsonResponse({
                'status': 'error',
                'mensaje': f'Esta venta ya se entregó el {venta.fecha_entrega.strftime("%d/%m/%Y %H:%M") if venta.fecha_entrega else "anteriormente"}.'
            })

        # Verificar el código
        if bcrypt.checkpw(codigo_cliente.encode(), venta.token_hash.encode()):
            venta.estatus = True
            venta.fecha_entrega = now()
            venta.save()
            return JsonResponse({'status': 'ok', 'mensaje': 'Código válido. Producto entregado.'})
        else:
            return JsonResponse({'status': 'error', 'mensaje': 'Código incorrecto. Verifica con el cliente.'})