def global_settings(request):
    # Ejemplo: carrito en sesión
    carrito = request.session.get(
        'carrito', [{}]
        )
    empresas_dict = request.session.get('empresas_dict', {})
    medidas = request.session.get('medidas', {})
    detalle_llanta = request.session.get('detalle_llanta', '')
 
    # Puedes agregar más variables globales aquí
    return {
        'carrito': carrito,
        'empresas_dict': empresas_dict,
        'medidas': medidas,
        'empresa': 'Mi Empresa',
        'moneda': 'MXN',
        'soporte_email': 'soporte@miempresa.com',
        'productos_seleccionados': len(carrito),
        'detalle_llanta': detalle_llanta,
    }