from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group, User
from appClinica.models import generarPassword
import threading

class RegistrarUsuarioTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_registrar_usuario_exitoso(self):
        data = {
            'txtNombres': 'Nombre Test',
            'txtApellidos': 'Apellido Test',
            'txtCorreo': 'test@example.com',
            'cbTipo': 'TipoUsuario1',
            'fileFoto': '',  
            'cbRol': 1, 
        }
        response = self.client.post(reverse('registrarUsuario'), data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/vistaGestionarUsuarios/')

        self.assertTrue(User.objects.filter(username='test@example.com').exists())

        user = User.objects.get(username='test@example.com')
        rol_administrador = Group.objects.get(name='Administrador')
        self.assertTrue(user.groups.filter(name='Administrador').exists())
        self.assertTrue(user.is_staff)

        self.assertEqual(len(threading.enumerate()), 1) 

   
