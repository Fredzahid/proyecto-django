import threading
from django.test import TransactionTestCase, TestCase
from django.db import transaction
from django.urls import reverse
from .models import Pelicula, Categoria, Cliente


class ConcurrenciaAlquilerTest(TransactionTestCase):
    # Tarea 8 - ejercicio 80 de las 100 tareas 
    # Simula a dos personas intentando alquilar la ÚLTIMA copia al mismo tiempo.
    def setUp(self):
        self.cat = Categoria.objects.create(nombre="Acción")
        self.pelicula = Pelicula.objects.create(
            titulo="Película Concurrente", 
            anio=2024,
            stock=1, 
            categoria=self.cat,
            precio_alquiler=10
        )
        self.cliente = Cliente.objects.create(nombre="Usuario Prueba", email="test@test.com")

    def intentar_alquilar(self):
        try:
            with transaction.atomic():
                p = Pelicula.objects.select_for_update().get(id=self.pelicula.id)
                if p.stock > 0:
                    import time
                    time.sleep(0.1)
                    p.stock -= 1
                    p.save()
        except Exception:
            pass

    def test_control_de_stock_concurrente(self):
        hilo1 = threading.Thread(target=self.intentar_alquilar)
        hilo2 = threading.Thread(target=self.intentar_alquilar)
        hilo1.start()
        hilo2.start()
        hilo1.join()
        hilo2.join()

        self.pelicula.refresh_from_db()
        self.assertEqual(self.pelicula.stock, 0)
        print(f"\n[TAREA 8 OK] Stock final: {self.pelicula.stock}. Concurrencia manejada.")

class ExportCSVTest(TestCase):
    # Tarea 9 - ejercicio 88
    # Verifica que el archivo CSV tenga el encabezado correcto.
    def test_csv_header(self):
        url = reverse('exportar_alquileres_csv')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

        content = response.content.decode('utf-8')
        lineas = content.splitlines()
        primer_linea = lineas[0]
        
        encabezado_esperado = "ID,Cliente,Pelicula,Fecha Alquiler,Pagado"
        self.assertEqual(primer_linea, encabezado_esperado)
        print(f"\n[TAREA 9 OK] Encabezado CSV verificado: {primer_linea}")


class RegressionBugsTest(TestCase):
    #Tarea 10 - ejercicio 90 de las 100 tareas
    #Lo que se hizo: Se creo la clase "RegressionBugsTest"
    #Que hara: intenta guardar una pelicula con año 3000 y veriica que el sistema 
    #realmente lo bloquea. Si el sistema lo permite, el test falla
    def setUp(self):
        self.cat = Categoria.objects.create(nombre="Acción")

    def test_bug_anio_futuro(self):
        """Bug: No permitir años irreales (ej. 3000)"""
        anio_loco = 3000
        pelicula = Pelicula(
            titulo="Viaje al Futuro", 
            anio=anio_loco, 
            categoria=self.cat, 
            precio_alquiler=10,
            stock=5
        )
        
        # Debe lanzar una excepción al validar
        with self.assertRaises(Exception):
            pelicula.full_clean() 
        print(f"\n[TAREA 10 OK] Bug de año futuro {anio_loco} capturado correctamente.")