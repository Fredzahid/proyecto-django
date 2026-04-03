from django.contrib import admin
from .models import Alquiler, Categoria, Cliente, Pelicula
# Importamos lo necesario para la Tarea 7 (Grupos)
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# --- 1. CONFIGURACIÓN VISUAL DEL ADMIN (Tu código actual) ---

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion"]
    search_fields = ["nombre"]

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "email", "telefono"]
    search_fields = ["nombre", "email"]

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "anio", "categoria", "precio_alquiler"]
    list_filter = ["categoria", "anio"]
    search_fields = ["titulo"]

@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ["fecha_alquiler", "cliente", "pelicula", "pagado", "precio", "fecha_devolucion"]
    list_filter = ["pagado", "fecha_alquiler", "fecha_devolucion"]
    search_fields = ["cliente__nombre", "pelicula__titulo"]


# TAREA 7 - ejercicio 62 de las 100 tareas
# Lo que se cambió: Se agregó esta lógica para crear roles de trabajo automáticamente.
# Qué hará: Al encender el servidor, Django creará los grupos "Cajeros" y "Supervisores" 
# con los permisos que definimos aquí abajo.

def crear_grupos_permisos():
    # Crear Grupo Cajeros (Solo puede alquilar y ver)
    cajeros, created = Group.objects.get_or_create(name='Cajeros')
    if created:
        permisos_cajero = Permission.objects.filter(
            codename__in=[
                'add_alquiler', 'view_alquiler', 
                'add_cliente', 'view_cliente',
                'view_pelicula'
            ]
        )
        cajeros.permissions.set(permisos_cajero)

    # Crear Grupo Supervisores (Control total de la tienda)
    supervisores, created = Group.objects.get_or_create(name='Supervisores')
    if created:
        # Buscamos todos los permisos que pertenecen a nuestra app 'tienda'
        tipo_contenido = ContentType.objects.filter(app_label='tienda')
        todos_permisos = Permission.objects.filter(content_type__in=tipo_contenido)
        supervisores.permissions.set(todos_permisos)

# Ejecutamos la función (con un try/except para evitar errores en la primera migración)
try:
    crear_grupos_permisos()
except:
    pass