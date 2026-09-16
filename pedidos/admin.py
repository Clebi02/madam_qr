from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Mesa, Plato, Pedido, DetallePedido

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'token', 'ver_qr')
    readonly_fields = ('token', 'qr_code')

    def ver_qr(self, obj):
        url = f"https://madam-qr.onrender.com/mesa/{obj.token}/"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={url}"
        return format_html('<img src="{}" width="60" height="60" />', qr_url)
    ver_qr.short_description = "Vista QR"

    def qr_code(self, obj):
        url = f"https://madam-qr.onrender.com/mesa/{obj.token}/"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
        return format_html(
            '<div style="text-align:center;">'
            '<img src="{}" /><br><br>'
            '<a class="button" href="{}" target="_blank">Probar enlace de la Mesa</a>'
            '</div>', 
            qr_url, url
        )
    qr_code.short_description = "Código QR para Imprimir"

admin.site.register(Categoria)
admin.site.register(Plato)
admin.site.register(Pedido)
admin.site.register(DetallePedido)