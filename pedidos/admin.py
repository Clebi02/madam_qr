from django.contrib import admin
from .models import Categoria, Mesa, Plato, Pedido, DetallePedido

admin.site.register(Categoria)
admin.site.register(Mesa)
admin.site.register(Plato)
admin.site.register(Pedido)
admin.site.register(DetallePedido)