from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views

urlpatterns = [
    #Tarea 3 - ejercicio 37 de las 100 tareas
    #Lo que se cambia: Se asigna la ruta raiz "path("",...)" a la funcion index.
    #Que hara: Permite que al entrar a la pagina principal se encargue automaticamente toda la logica de los KPIs que se definio.
    path("", views.index, name="index"),
    # Categorias
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nueva/", views.CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria_update"),
    path("categorias/<int:pk>/eliminar/", views.CategoriaDeleteView.as_view(), name="categoria_delete"),
    # Peliculas
    path("peliculas/", views.PeliculaListView.as_view(), name="pelicula_list"),
    path("peliculas/nueva/", views.PeliculaCreateView.as_view(), name="pelicula_create"),
    path("peliculas/<int:pk>/editar/", views.PeliculaUpdateView.as_view(), name="pelicula_update"),
    path("peliculas/<int:pk>/eliminar/", views.PeliculaDeleteView.as_view(), name="pelicula_delete"),
    # Clientes
    path("clientes/", views.ClienteListView.as_view(), name="cliente_list"),
    path("clientes/nuevo/", views.ClienteCreateView.as_view(), name="cliente_create"),
    path("clientes/<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="cliente_update"),
    path("clientes/<int:pk>/eliminar/", views.ClienteDeleteView.as_view(), name="cliente_delete"),
    # Alquileres
    path("alquileres/", views.AlquilerListView.as_view(), name="alquiler_list"),
    path("alquileres/nuevo/", views.AlquilerCreateView.as_view(), name="alquiler_create"),
    path(
        "alquileres/<int:pk>/marcar-pagado/",
        views.MarcarPagadoView.as_view(),
        name="alquiler_marcar_pagado",
    ),
    #login
    #Tarea 7 - ejercicio 62 de las 100 tareas
    #Se importo "auth_views" y se añadieron las rutas de "login/" y "logout/"
    #Que hara: activa las "puertas" del sistema. Sin esto el boton de "Entrar" o "Salir" daria un error de pagina no encontrada 
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #Tarea 9 - ejercicio 80 de las 100 tareas
    #Se registro una nueva Ruta(path) que permite a cualquier usuario o sistema externo descargar el reporte simplemente a una direccion web
    #Que hara: Crea el enlace o "puerta de acceso" para que el usuario o el sistema de pruebas pueda descargar el archivo de reporte 
    path('alquileres/csv/', views.exportar_alquileres_csv, name='exportar_alquileres_csv'),
    #Ventas (en esta versión: alquileres pagados)
    path("ventas/", views.VentasListView.as_view(), name="ventas_list"),
    path("ventas/simular/", views.simular_ventas, name="ventas_simular"),
]

