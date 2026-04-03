#Tarea 11 - ejercicio 97 de las 100 tareas
#Que se hizo: se añadio el metodo "ready()"
#Que hara: conecta tus chequeos personalizados con el nucleo de Django al iniciar el servidor

from django.apps import AppConfig

class TiendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tienda'

    def ready(self):
        # Importamos el archivo de checks para que se registre el decorador @register
        import tienda.checks