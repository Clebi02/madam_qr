import json
import math
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Mesa, Plato, Categoria, Pedido, DetallePedido

RESTAURANTE_LAT = -12.046374 
RESTAURANTE_LON = -77.042793
DISTANCIA_MAXIMA_METROS = 50.0

def calcular_distancia_metros(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def menu_vista(request, token):
    mesa = get_object_or_404(Mesa, token=token)
    categorias = Categoria.objects.prefetch_related('platos').all().order_by('orden')
    return render(request, 'pedidos/menu.html', {'mesa': mesa, 'categorias': categorias})

@csrf_exempt
def crear_pedido_api(request, token):
    if request.method == 'POST':
        mesa = get_object_or_404(Mesa, token=token)
        data = json.loads(request.body)
        items = data.get('items', [])
        lat_user = data.get('lat')
        lon_user = data.get('lon')

        if lat_user is None or lon_user is None:
            return JsonResponse({'ok': False, 'error': 'Debes activar el GPS para pedir.'}, status=400)
        
        distancia = calcular_distancia_metros(RESTAURANTE_LAT, RESTAURANTE_LON, float(lat_user), float(lon_user))
        if distancia > DISTANCIA_MAXIMA_METROS:
            return JsonResponse({
                'ok': False, 
                'error': f'Estás fuera del restaurante ({int(distancia)}m). Límite: 50m.'
            }, status=403)

        if not items:
            return JsonResponse({'ok': False, 'error': 'Carrito vacío'}, status=400)

        # Buscar comanda activa de la mesa para anexar o crear nueva
        pedido = Pedido.objects.filter(
            mesa=mesa, 
            estado__in=['pendiente', 'preparacion']
        ).first()

        if not pedido:
            pedido = Pedido.objects.create(mesa=mesa, estado='pendiente', total=0)

        monto_adicional = 0
        for item in items:
            plato = get_object_or_404(Plato, id=item['id'])
            cant = int(item['cantidad'])
            sub = plato.precio * cant
            monto_adicional += sub
            DetallePedido.objects.create(pedido=pedido, plato=plato, cantidad=cant, subtotal=sub)

        pedido.total = float(pedido.total) + float(monto_adicional)
        pedido.save()
        
        return JsonResponse({'ok': True, 'pedido_id': pedido.id})

    return JsonResponse({'ok': False}, status=400)

def cocina_vista(request):
    return render(request, 'pedidos/cocina.html')

def cocina_api(request):
    # Trae todos los pedidos activos (que no estén entregados ni cancelados)
    pedidos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado']).order_by('creado_en')
    data = []
    for p in pedidos:
        detalles = [f"{d.cantidad}x {d.plato.nombre}" for d in p.detalles.all()]
        data.append({
            'id': p.id,
            'mesa': p.mesa.numero,
            'estado': p.get_estado_display(),
            'estado_raw': p.estado,
            'total': str(p.total),
            'hora': p.creado_en.strftime('%H:%M'),
            'detalles': detalles
        })
    return JsonResponse({'pedidos': data})

@csrf_exempt
def cambiar_estado_api(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        data = json.loads(request.body)
        pedido.estado = data.get('nuevo_estado', 'entregado')
        pedido.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)