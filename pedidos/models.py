import uuid
from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

class Plato(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='platos', null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)
    imagen_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Mesa {self.numero}"

class Pedido(models.Model):
    ESTADOS = [
        ('por_confirmar', 'Por Confirmar'),
        ('pendiente', 'Pendiente (Cocina)'),
        ('preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='por_confirmar')
    creado_en = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido #{self.id} - Mesa {self.mesa.numero} ({self.estado})"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=6, decimal_places=2)