from __future__ import annotations

import datetime

from django import forms

from .models import Alquiler, Categoria, Cliente, Pelicula


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "email", "telefono"]

#tarea 2 - ejercicio 21 de las 100 tareas
#lo que se cambia: Se añadio el metodo "clean_anio" dentro de la clase "PeliculaForm".
#Que hara: Obtendra el año actual del sistema y comparara el valor ingresado; si es mayor, dentendra el guardado y lanzara un mensaje de error.
class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ["titulo", "anio", "categoria", "precio_alquiler"]

    #SE AGREGA...
    def clean_anio(self):
        #1. Recuperamosv el valor que el usuario escribio en el formulario
        anio_ingresado = self.cleaned_data.get("anio")
        #2. Obtenemos el año actual
        anio_actual = datetime.date.today().year
        #3. Logica de validacion 
        if anio_ingresado and anio_ingresado > anio_actual:
            #si el año es mayor al actual, se lanza error
            raise forms.ValidationError(
                f"El año no puede ser mayor al actual ({anio_actual})."
            )
        #4. Siempre se debe retornar el valor limpio
        return anio_ingresado


class AlquilerCreateForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ["cliente", "pelicula"]


class MarcarPagadoForm(forms.Form):
    fecha_devolucion = forms.DateField(
        required=False,
        label="Fecha de devolución (opcional)",
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class SimularVentasForm(forms.Form):
    numero_ventas = forms.IntegerField(min_value=1, max_value=200, label="Cantidad de ventas a simular")
    desde = forms.DateField(required=False, label="Desde (opcional)", widget=forms.DateInput(attrs={"type": "date"}))
    hasta = forms.DateField(required=False, label="Hasta (opcional)", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super().clean()
        desde = cleaned.get("desde")
        hasta = cleaned.get("hasta")

        if desde and hasta and desde > hasta:
            raise forms.ValidationError("La fecha 'Desde' no puede ser posterior a 'Hasta'.")

        # Si no se manda rango, usaremos la fecha de hoy.
        if not desde and not hasta:
            today = datetime.date.today()
            cleaned["desde"] = today
            cleaned["hasta"] = today

        return cleaned

