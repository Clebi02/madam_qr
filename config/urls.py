from django.contrib import admin
from django.urls import path
from pedidos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mesa/<uuid:token>/', views.menu_vista, name='menu'),
    path('api/pedido/<uuid:token>/', views.crear_pedido_api, name='crear_pedido_api'),
    path('mozo/', views.mozo_vista, name='mozo'),
    path('api/mozo/', views.mozo_api, name='mozo_api'),
    path('cocina/', views.cocina_vista, name='cocina'),
    path('api/cocina/', views.cocina_api, name='cocina_api'),
    path('api/pedido/estado/<int:pedido_id>/', views.cambiar_estado_api, name='cambiar_estado_api'),
]