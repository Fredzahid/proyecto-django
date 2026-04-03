import datetime
import random
import csv # <--- se añade este import - tarea 9 - ejercicio 88 de las 100 tareas

from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.db import transaction # <--- se añade este import - Tarea 8 - ejercicio 80 de las 100 tareas 
from django.core.cache import cache # <--- se añade este import - Tarea 5 - ejercicio 48 de las 100 tareas
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AlquilerCreateForm, MarcarPagadoForm, SimularVentasForm, PeliculaForm
from .models import Alquiler, Categoria, Cliente, Pelicula


def index(request: HttpRequest) -> HttpResponse:
    #Intentamos obtener los datos del cache
    datos_cache = cache.get("dashboard_metrics")
    #Si no estan en cache, lo calculamos y guardamos
    if datos_cache is None:
        total_peliculas = Pelicula.objects.count()
        total_clientes = Cliente.objects.count()
        alquileres_pendientes = Alquiler.objects.filter(pagado=False).count()
        ingresos = (
            Alquiler.objects.filter(pagado=True)
            .aggregate(total=Sum("precio"))
            .get("total") or 0
        )
        #Metemos todo en el diccionario que vamos a cachear
        datos_cache = {
            "total_peliculas": total_peliculas,
            "total_clientes": total_clientes,
            "alquileres_pendientes": alquileres_pendientes,
            "ingresos": ingresos,
        }
        #Guardamos en cache por 60 segundos
        cache.set("dashboard_metrics", datos_cache, 60)
    #Tarea 3 - ejercicio 37 de las 100 tareas
    #Lo que se cambio: se definieron las variables dentro de la funcion "index" usando metodos de agregacion (sum) y conteo (count).
    #Que hara: Consulta la base de datos para obtener los numeros reales del negocio y los envia al diccionario de contexto.
    return render(request, "tienda/index.html", datos_cache)
    #lo de arriba tambien es la Tarea 5 - ejercicio 48 de las 100 tareas
    #Lo que se cambio: se envolvio la logica de calculo del Dashboard dentro de un bloque "if cache.get("Dashboard_metrics") is None:. Ademas, se cambio el "return render" para que use directamente el diccionario "datos_cache" 
    #Que hace: el servidor hace 4 consultas a la base de datos (contar peliculas, clientes, alquileres y sumar ingresos), guarda l resultado en la memoria RAM y lo muestra 

class CategoriaListView(ListView):
    model = Categoria
    template_name = "tienda/categoria_list.html"
    context_object_name = "categorias"


class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = None  # se usa el form del modelo con campos del template
    fields = ["nombre", "descripcion"]
    template_name = "tienda/categoria_form.html"
    success_url = reverse_lazy("categoria_list")


class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = None
    fields = ["nombre", "descripcion"]
    template_name = "tienda/categoria_form.html"
    success_url = reverse_lazy("categoria_list")


class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = "tienda/categoria_confirm_delete.html"
    success_url = reverse_lazy("categoria_list")


class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"


class ClienteCreateView(CreateView):
    model = Cliente
    fields = ["nombre", "email", "telefono"]
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("cliente_list")


class ClienteUpdateView(UpdateView):
    model = Cliente
    fields = ["nombre", "email", "telefono"]
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("cliente_list")


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "tienda/cliente_confirm_delete.html"
    success_url = reverse_lazy("cliente_list")


class PeliculaListView(ListView):
    model = Pelicula
    template_name = "tienda/pelicula_list.html"
    context_object_name = "peliculas"

#tarea 1 - ejercicio 21 de las 100 tareas 
#Lo que se cambia: En las clases "PeliculasCreateView" y "PeliculaUpdateView", se sustitye el atributo "fields" por "form_class = PeliculaForm".
#Que hara: Obligara a Django a usar el formulario personalizado en lugar del generico, activando asi la validacion del año que se programo.
class PeliculaCreateView(CreateView):
    model = Pelicula
    form_class = PeliculaForm # <--- Este es el cambio 
    template_name = "tienda/pelicula_form.html"
    success_url = reverse_lazy("pelicula_list")

#tarea 4 - ejercicio 47 de las 100 tareas
#Lo que se cambia: se sobrescribe el metodo "get_success_url" en la vista (por ejemplo, PeliculaUpdateView).
#Que hara: Le dice a Django: "Si hay una direccion en el campo "next", ve hacia alla despues de guardar. Si no, usa la ruta por efecto"
class PeliculaUpdateView(UpdateView):
    model = Pelicula
    form_class = PeliculaForm
    template_name = "tienda/pelicula_form.html"
    
    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pelicula_list")


class PeliculaDeleteView(DeleteView):
    model = Pelicula
    template_name = "tienda/pelicula_confirm_delete.html"
    success_url = reverse_lazy("pelicula_list")


class AlquilerCreateView(CreateView):
    model = Alquiler
    form_class = AlquilerCreateForm
    template_name = "tienda/alquiler_form.html"
    success_url = reverse_lazy("alquiler_list")

#Tarea 8 - ejercicio 80 de las 100 tareas 
#Lo que se cambio: se sobrescribio el metodo form_valid con un bloque 
#transaction.atomic() y se uso select_for_update() en la pelicula
#Que hara: Bloquea la fila de la pelicula en la DB hasta que se encuentre el stock,
#evitando que dos personas alquilen la misma copia simultaneamente
    def form_valid(self, form):
        try: 
            with transaction.atomic():
                pelicula = Pelicula.objects.select_for_update().get(id=form.cleaned_data['pelicula'].id)
                
                if pelicula.stock > 0:
                    # Corregido: super().form_valid (era form_valid, no from_valid)
                    response = super().form_valid(form)
                    pelicula.stock -= 1
                    pelicula.save()
                    return response
                else:
                    form.add_error('pelicula', "Lo sentimos, No hay stock disponible de esta película.")
                    return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Error de base de datos: {e}")
            return self.form_invalid(form)

class AlquilerListView(ListView):
    model = Alquiler
    template_name = "tienda/alquiler_list.html"
    context_object_name = "alquileres"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("cliente", "pelicula", "pelicula__categoria")
        pagado = self.request.GET.get("pagado")
        if pagado == "1":
            qs = qs.filter(pagado=True)
        elif pagado == "0":
            qs = qs.filter(pagado=False)
        return qs


class MarcarPagadoView(View):
    template_name = "tienda/marcar_pagado.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        alquiler = get_object_or_404(Alquiler, pk=pk)
        form = MarcarPagadoForm()
        return render(request, self.template_name, {"alquiler": alquiler, "form": form})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        alquiler = get_object_or_404(Alquiler, pk=pk)
        form = MarcarPagadoForm(request.POST)
        if form.is_valid():
            alquiler.marcar_pagado(fecha_devolucion=form.cleaned_data.get("fecha_devolucion"))
            return redirect("alquiler_list")
        return render(request, self.template_name, {"alquiler": alquiler, "form": form})


class VentasListView(ListView):
    model = Alquiler
    template_name = "tienda/ventas_list.html"
    context_object_name = "ventas"

    def get_queryset(self):
        return (
            Alquiler.objects.filter(pagado=True)
            .select_related("cliente", "pelicula", "pelicula__categoria")
            .order_by("-fecha_alquiler")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_ingresos"] = self.get_queryset().aggregate(total=Sum("precio")).get("total") or 0
        return ctx


def simular_ventas(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SimularVentasForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero_ventas"]
            desde = form.cleaned_data["desde"]
            hasta = form.cleaned_data["hasta"]

            clientes = list(Cliente.objects.all())
            peliculas = list(Pelicula.objects.all())

            if not clientes or not peliculas:
                return render(
                    request,
                    "tienda/simular_ventas.html",
                    {"form": form, "error": "Necesitas al menos 1 cliente y 1 película para simular."},
                )

            # Generamos fechas aleatorias en el rango.
            alquileres_creados = 0
            delta_dias = (hasta - desde).days if hasta >= desde else 0

            for _ in range(numero):
                cliente = random.choice(clientes)
                pelicula = random.choice(peliculas)

                offset = random.randint(0, max(delta_dias, 0))
                fecha_alquiler = desde + datetime.timedelta(days=offset)

                # En esta versión simple, una "venta" es un alquiler marcado como pagado.
                fecha_devolucion = fecha_alquiler + datetime.timedelta(days=random.randint(0, 7))
                Alquiler.objects.create(
                    cliente=cliente,
                    pelicula=pelicula,
                    fecha_alquiler=fecha_alquiler,
                    pagado=True,
                    fecha_devolucion=fecha_devolucion,
                )
                alquileres_creados += 1

            return redirect("ventas_list")
    else:
        form = SimularVentasForm(
            initial={
                "numero_ventas": 10,
                "desde": timezone.localdate(),
                "hasta": timezone.localdate(),
            }
        )


    return render(request, "tienda/simular_ventas.html", {"form": form})

#Tarea 9 - ejercicio 88 de las 100 tareas
#Que se cambio: se creo la funcion "exportar_alquileres_csv" con un encabezado fijo.
#Que hara: transformar los datos de la base de datos en un archivo "Excel/CSV" descargable para reportes
def exportar_alquileres_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alquileres.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Pelicula', 'Fecha Alquiler', 'Pagado'])

    alquileres = Alquiler.objects.all()
    for a in alquileres:
        writer.writerow([a.id, a.cliente.nombre, a.pelicula.titulo, a.fecha_alquiler, a.pagado])

    return response