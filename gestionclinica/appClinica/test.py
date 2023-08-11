from django.test import TestCase, Client
from django.urls import reverse
from .models import Servicios

class AgregarServicioTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_agregar_servicio_nuevo(self):
        data = {
            'serNombre': 'Nuevo Servicio',
            'serTipo': 'Urgencias',
        }
        response = self.client.post(reverse('agregarServicio'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/vistaGestionarServicios/')
        self.assertTrue(Servicios.objects.filter(serNombre='Nuevo Servicio', serTipo='Urgencias').exists())

    def test_agregar_servicio_existente(self):
        Servicios.objects.create(serNombre='Servicio Existente', serTipo='ServicioBasico')
        data = {
            'serNombre': 'Servicio Existente',
            'serTipo': 'ServicioBasico',
        }
        response = self.client.post(reverse('agregarServicio'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ya existe un servicio con este nombre")
        self.assertFalse(Servicios.objects.filter(serNombre='Servicio Existente', serTipo='ServicioBasico').exists())