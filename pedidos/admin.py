from django.contrib import admin
from .models import Categoria, Mesa, Plato, Pedido, DetallePedido

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'token')
    readonly_fields = ('token',)

admin.site.register(Categoria)
admin.site.register(Plato)
admin.site.register(Pedido)
admin.site.register(DetallePedido)