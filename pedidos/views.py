import json
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Mesa, Plato, Categoria, Pedido, DetallePedido

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
        if not items:
            return JsonResponse({'ok': False, 'error': 'Carrito vacío'}, status=400)
        
        pedido = Pedido.objects.create(mesa=mesa, total=0)
        monto_total = 0
        for item in items:
            plato = get_object_or_404(Plato, id=item['id'])
            cant = int(item['cantidad'])
            sub = plato.precio * cant
            monto_total += sub
            DetallePedido.objects.create(pedido=pedido, plato=plato, cantidad=cant, subtotal=sub)
        
        pedido.total = monto_total
        pedido.save()
        return JsonResponse({'ok': True, 'pedido_id': pedido.id})
    return JsonResponse({'ok': False}, status=400)

def cocina_vista(request):
    return render(request, 'pedidos/cocina.html')

def cocina_api(request):
    pedidos = Pedido.objects.exclude(estado__in=['entregado', 'cancelado']).order_by('creado_en')
    data = []
    for p in pedidos:
        detalles = [f"{d.cantidad}x {d.plato.nombre}" for d in p.detalles.all()]
        data.append({
            'id': p.id,
            'mesa': p.mesa.numero,
            'estado': p.estado,
            'hora': p.creado_en.strftime('%H:%M'),
            'detalles': detalles
        })
    return JsonResponse({'pedidos': data})

@csrf_exempt
def cambiar_estado_api(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('nuevo_estado', 'entregado')
        pedido.estado = nuevo_estado
        pedido.save()

        # Si el pedido es entregado/culminado, renovamos el token de la mesa para el siguiente cliente
        if nuevo_estado == 'entregado':
            pedido.mesa.token = uuid.uuid4()
            pedido.mesa.save()

        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)