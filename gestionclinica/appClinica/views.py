from django.shortcuts import render, redirect
from appClinica.models import *
from django.http import HttpResponse
import random
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login as auth_login
from django.db import Error, transaction
from django.contrib import auth
from django.http import JsonResponse
from datetime import date, datetime
import string
from django.contrib.auth import authenticate
from django.conf import settings
import urllib
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
import matplotlib.pyplot as plt
from .models import CitaVeterinaria, Mascota,AgendarCita, User, Servicios
import os
#from fpdf import FPDF
#from appClinica.pdfSolicitudes import PDF


datosSesion = {"user": None, "rutaFoto": None, "rol": None}

# Create your views here.

def inicioAdministrador(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                    "rol": request.user.groups.get().name}
        return render(request, "administrador/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        retorno = {"roles": roles, "user": request.user,
                "rol": request.user.groups.get().name}
        return render(request, "administrador/frmRegistrarUsuario.html")
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto", False)
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            # crear un objeto de tipo User
            user = User(username=correo, first_name=nombres,last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            # obtener el Rol de acuerdo a id del rol
            rol = Group.objects.get(pk=idRol)
            # agregar el usuario a ese Rol
            user.groups.add(rol)
            # si el rol es Administrador se habilita para que tenga acceso al sitio web del administrador
            if (rol.name == "Administrador"):
                user.is_staff = True 
            # se guarda el usuario con los datos que hay
            user.save()
            # se llama a la funcion generarPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            # con el usuario creado se llama a la función set_password #que encripta el password y lo agrega al campo password del #user.
            user.set_password(passwordGenerado)
            # se actualiza el user
            user.save()
            mensaje = "Usuario Agregado Correctamente"
            retorno = {"mensaje": mensaje}
            # enviar correo al usuario
            asunto = 'Registro Usuario VetAnimals'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema gestion de la clinica Veterinaria VetAnimals \
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestionUsuario.VetAnimals.co.'
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)

def generarPassword():
    """
    Genera un password de longitud de 10 que incluye letras mayusculas
    y minusculas,digitos y cararcteres especiales
    Returns:
        _str_: retorna un password
    """
    longitud = 10

    caracteres = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    password = ''

    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)

def vistaGestionarUsuarios(request):
    if request.user.is_authenticated:
        usuarios = User.objects.all()
        retorno = {"usuarios": usuarios, "user": request.user,
                "rol": request.user.groups.get().name}
        return render(request, "administrador/vistaGestionarUsuarios.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def vistaLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user = User.objects.get(user=user)
            if user.userTipo in ['administrador', 'veterinario', 'auxiliar']:
                return redirect('/inicio')  # Redirigir a la página de inicio para personal
            elif user.userTipo == 'cliente':
                return redirect('/vistaRegistrarUsuarioCliente')  # Redirigir a la página de inicio para clientes
        else:
            # Manejar el caso de credenciales inválidas
            return render(request, 'frmIniciarSesion.html', {'error_message': 'Credenciales inválidas'})
    else:
        return render(request, 'frmIniciarSesion.html')

def login(request,urlReturn=""):
    # validar el recapthcha
    """Begin reCAPTCHA validation"""
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    """ End reCAPTCHA validation """
    if result['success']:
        username = request.POST["txtUsername"]
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # registrar la variable de sesión
            auth.login(request, user)
            #if urlReturn!="":
                #return redirect(urlReturn)
            #else:
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Especialista').exists():
                return redirect('/inicioEspecialista')
            elif user.groups.filter(name='Tecnico').exists():
                return redirect('/inicioTecnico')
            else:
                return redirect('/inicioCliente')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    else:
        mensaje = "Debe validar primero el recaptcha"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def agregarServicio(request):
    tipoServicio = [
        ('ServicioBasico', "ServicioBasico"),
        ('ServicioBienestar', "ServicioBienestar"),
        ('Urgencias', "Urgencias"),
        ('OtrosServicios', "OtrosServicios"),
    ]

    if request.method == 'POST':
        # Obtener los datos del formulario
        serNombre = request.POST.get('serNombre')
        serTipo = request.POST.get('serTipo')

        if Servicios.objects.filter(serNombre=serNombre).exists():
            error_message = "Ya existe un servicio con este nombre. Por favor, elige otro."
            print(error_message) 
            
            return render(request, 'administrador/agregarServicio.html', {'tipoServicio': tipoServicio, 'error_message': error_message})
        else :
            # Si no existe un servicio con el mismo nombre, creamos uno nuevo
            nuevoServicio = Servicios(serNombre=serNombre, serTipo=serTipo)
            nuevoServicio.save()

            # Redireccionar a la página de éxito o a donde desees después de crear el servicio.
            return redirect('/vistaGestionarServicios/')  #  el nombre de tu página de éxito.

    # Si es una solicitud GET, simplemente renderizar el formulario.
    return render(request, 'agregarServicio.html', {'tipoServicio': tipoServicio})

def vistaAgregarServicio(request):
    retorno={"tipoServicio":tipoServicio}
    return render(request,"administrador/agregarServicio.html",retorno)

def vistaGestionarServicios(request):   
    servicios=Servicios.objects.all()
    retorno = {"listaServicios":servicios} 
    return render(request, 'administrador/agregarServicio.html', retorno)

def salir(request):
    auth.logout(request)
    return render(request, "frmIniciarSesion.html",
                {"mensaje": "Ha cerrado la sesión"})
    


def inicioCliente(request):
    return render(request, "cliente/inicio.html")
    
def vistaLoginCliente(request):
        return render(request, "cliente/frmIniciarSesionCliente.html")

def viewRUsuarioCliente(request):
        return render(request, "cliente/frmRegistrarUsuarioCliente.html")

def loginCliente(request, urlReturn=""):
    # validar el recaptcha
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())

    if result['success']:
        if request.method == 'POST':
            username = request.POST["txtUsername"]
            password = request.POST["txtPassword"]
            user = authenticate(username=username, password=password)

            if user is not None:
                auth_login(request, user)
                if urlReturn != "":
                    return redirect(urlReturn)
                else:
                    if user.groups.filter(name='Cliente').exists():
                        return redirect('/vistaRegistrarMascota')
                    elif user.groups.filter(name='Especialista').exists():
                        return redirect('/inicioEspecialista')
                    elif user.groups.filter(name='Tecnico').exists():
                        return redirect('/inicioTecnico')
                    else:
                        return redirect('/inicioAdministrador')
            else:
                mensaje = "Usuario o Contraseña Incorrectas"
                return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    else:
        mensaje = "Debe validar primero el reCAPTCHA"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

    return render(request, "frmIniciarSesion.html")

def vistaRegistrarUsuarioCliente(request):
    if request.user.is_authenticated:
        # Verificar si el usuario ya está registrado como cliente
        if request.user.groups.filter(name='Cliente').exists():
            # Mostrar la vista de agendamiento de cita
            if request.method == 'POST':
                agendar = AgendarCita(request.POST)
                if agendar.is_valid():
                    # Procesar el formulario de agendamiento de cita
                    mensaje = "Cita agendada exitosamente"
                else:
                    mensaje = "Error en el formulario de agendamiento"
            else:
                agendar = AgendarCita()
            return render(request, "cliente/vistaRegistrarUsuarioCliente.html", {"agendar": agendar, "user": request.user})
        else:
            # Redirigir al formulario de registro
            return redirect("/vistaRegistrarUsuarioCliente/")

    else:
        # Redirigir a la vista de login
        return redirect("/vistaLogin/")

def vistaUsuarioCliente(request):
    if request.user.is_authenticated:
        # Verifica si el usuario ya está registrado como cliente
        if request.user.groups.filter(name='Cliente').exists():
            # Muestra la vista de agendamiento de cita
            if request.method == 'POST':
                agendacita = AgendarCita(request.POST)
                if agendacita.is_valid():
                    mensaje = "Cita agendada exitosamente"
            else:
                    mensaje = "Error en el formulario de agendamiento"
        else:
            agendacita = AgendarCita()

        return render(request, "vistaAgendarCita.html", {"agendacita": agendacita, "user": request.user})

    else:
        # Redirigir al formulario de registro
        return redirect("/vistaRegistrarUsuarioCliente/")

def registrarUsuarioCliente(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=correo).exists():
            mensaje = "El usuario ya está registrado"
            retorno = {"mensaje": mensaje}
            return render(request, "cliente/frmRegistrarUsuarioCliente.html", retorno)

        with transaction.atomic():
            # Crear el objeto de tipo User con los datos de registro del cliente
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo)
            user.set_unusable_password()  # Para evitar problemas con la contraseña
            user.save()
            # Asignar el rol de "Cliente" al usuario registrado
            grupo_cliente = Group.objects.get(name='Cliente')
            user.groups.add(grupo_cliente)
            # Guardar el usuario con los datos que hay
            user.save()
            # se llama a la funcion generarPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            # con el usuario creado se llama a la función set_password #que encripta el password y lo agrega al campo password del #user.
            user.set_password(passwordGenerado)
            # se actualiza el user
            user.save()
            mensaje = "Cliente Agregado Correctamente"
            retorno = {"mensaje": mensaje}
            # enviar correo al usuario
            asunto = 'Registro Usuario VetAnimals'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema gestion de la clinica Veterinaria VetAnimals \
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestionClinica.VetAnimals.co.'
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            return redirect("/vistaLoginCliente/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje}
    return render(request, "cliente/frmRegistrarUsuarioCliente.html", retorno)


def vistaGestionarMascotas(request):
    if request.user.is_authenticated:
        mascotas = Mascota.objects.all()
        retorno = {"mascotas": mascotas,
                   "user": request.user, "rol": request.user.groups.get().name}
        return render(request, "administrador/vistaGestionarMascotas.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def vistaRegistrarMascota(request):
    if request.user.is_authenticated:
        retorno = {
            "especie": especie, 
            "sexoMascota": sexoMascota, 
            "mascotas": Mascota.objects.filter(masCliUsuario = request.user),
            "user": request.user,
            "rol": request.user.groups.get().name}
        return render(request, "cliente/frmRegistrarMascota.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def registrarMascota(request):
    estado = False
    try:
        # datos de la mascota en general
        nombreMas = request.POST['txtNombre']
        especieMas = request.POST['cbEspecie']
        razaMas = request.POST['txtRaza']
        colorMas = request.POST['txtColor']
        sexoMas = request.POST['cbSexo']
        nacimientoFecha = request.POST.get('txtFecha')
        print(request.user)
        foto = request.FILES.get("fileFoto", False)
        mascota = None
        with transaction.atomic():
            cantidad = Mascota.objects.all().count()
            # crear un codigo a partir de la cantidad, ajustando 0 al inicio
            codigoMascota = especieMas.upper() + str(cantidad+1).rjust(5, '0')
            usuario = request.user
            mascota = Mascota(masCliUsuario= usuario,
                masCodigo=codigoMascota,masNombre=nombreMas, masEspecie=especieMas, masRaza=razaMas, masColor=colorMas, masSexo=sexoMas, masFechaNacimiento=nacimientoFecha, masFoto=foto)
            # salvar el elemento en la base de datos
            mascota.save()
            estado = True
            mensaje = f"Mascota registrada correctamente con el codigo {codigoMascota}"
            return redirect("/vistaAgendarCita/")
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje": mensaje, "mascota": mascota}
    return render(request, "cliente/frmRegistrarMascota.html", retorno)

def vistaGestionarCitasAgendadas(request):
    return render(request, 'cliente/vistaGestionarCitasAgendadas.html', {
        'agendarCita': AgendarCita.objects.all(),
    })
    
def vistaAgendarCita(request):
    if request.user.is_authenticated:
        mascotas = Mascota.objects.filter(masCliUsuario=request.user)
        servicios = Servicios.objects.all()
        tipoServicios = [servicio.serNombre for servicio in servicios]
        retorno = {"listaMascotas":mascotas, "tipoServicios": tipoServicios, "servicios": servicios}
        print(retorno)
        return render(request, "cliente/frmAgendarCita.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})


   
def agendarCita(request):
    if(request.user.is_authenticated):
        if request.method == "POST":
            mascota_id = request.POST.get('cbNombreMascota')
            servicio_id = request.POST.get('cbServicio')
            fechaCita = request.POST.get('txtFecha')
            if servicio_id:
                try:
                    # Obtener los objetos de Mascota y Servicios
                    mascota = Mascota.objects.get(pk=mascota_id)
                    servicio = Servicios.objects.get(pk=servicio_id)
                    # Crear la nueva cita
                    cita = AgendarCita(ageCitMascota=mascota, ageCitTipServicios=servicio, fechaHoraCita=fechaCita)
                    cita.save()
                    return redirect('/inicioCliente/')
                        
                except (Mascota.DoesNotExist, Servicios.DoesNotExist):
                        # Manejar el caso si no se encuentra la mascota
                    mensaje = 'La mascota no existe, por favor registrela primero'
                    mascotas = Mascota.objects.all()
                    servicios = Servicios.objects.all()
                    return render(request, 'frmAgendarCita.html', {'mascotas': mascotas, 'servicios': servicios, 'mensaje': mensaje})#formulario para agendar la cita
            else:
                mensaje = 'Seleccione un Tipo de Servicio válido'
                mascotas = Mascota.objects.all()
                servicios = Servicios.objects.all()
                return render(request, 'frmAgendarCita.html', {'mascotas': mascotas, 'servicios': servicios, 'mensaje': mensaje})
        #else:
          #  mensaje = "Debe iniciar sesión"
           # return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})



def inicioEspecialista(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                    "rol": request.user.groups.get().name}
        return render(request, "especialista/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    
def vistaGestionarCitasVeterinarias(request):
    if request.user.is_authenticated:
        retorno = {"citasAgendadas": AgendarCita.objects.all(),
                "citasVeterinarias": CitaVeterinaria.objects.all(),
                "user": request.user,
                "rol": request.user.groups.get().name}
        return render(request, "especialista/vistaGestionarCitasVeterinarias.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    
def vistaRegistrarCitaVeterinaria(request):
    if request.user.is_authenticated:
        retorno = {"estadoCitas": estadoCita, "user": request.user,
                "rol": request.user.groups.get().name}
        return render(request, "especialista/frmRegistrarCitaVeterinaria.html", retorno)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

def registrarCitaVeterinaria(request):
    if request.method == 'POST':
        estado = False
        mensaje = ""

        try:
            with transaction.atomic():
                # Datos de la cita veterinaria
                codigoCita = request.POST.get('txtCodigo', '')
                nombreMas = request.POST.get('txtNombre','')
                acompananteCita = request.POST.get('txtAcompanante', '')
                resultadoCita = request.POST.get('txtResultado', '')
                estadoCita = request.POST.get('cbEstado', '')
                precioCita = float(request.POST.get('txtPrecio', 0))
                fechaHora = request.POST.get('txtFechaHora', '')
                # Obtener el cliente y la mascota asociada a la cita
                masCodigo = request.POST.get('masCodigo', None)
                cliente = None
                mascota = Mascota.objects.get(pk=masCodigo)
                cita = CitaVeterinaria.objects.get(pk=codigoCita)
                #cliente = cita.citVetUserCliente.
                # Obtener el usuario actual (que debe estar autenticado)
                usuario_actual = request.user
                # Hacer un "inner join" para obtener los datos del veterinario
                veterinario = User.objects.select_related('veterinario').get(pk=usuario_actual.pk).veterinario 
                # Hacer un "inner join" para obtener los datos del cliente
                cliente = User.objects.select_related('cliente').get(pk=usuario_actual.pk).cliente   
                # Verificar si el usuario actual es un cliente
                
                cliente = User.request.user.groups.filter(name='Cliente')
                # Crear la cita veterinaria
                citaVeterinaria = CitaVeterinaria(
                    citVetCodigo=codigoCita,
                    citVetAcompanante=acompananteCita,
                    cliente=cliente,
                    mascota=mascota,
                    veterinario=veterinario, # Si se obtiene el veterinario a partir del usuario actual
                    citVetResultado=resultadoCita,
                    citVetEstado=estadoCita,
                    citPrecio=precioCita,
                    fechaHoraCreacion=fechaHora
                )

                # Registrar en la base de datos la cita veterinaria
                citaVeterinaria.save()

                estado = True
                mensaje = f"Cita veterinaria registrada satisfactoriamente con el código {codigoCita}"

        except Exception as e:
            transaction.rollback()
            mensaje = f"Error al registrar la cita veterinaria: {e}"

        retorno = {
            "mensaje": mensaje,
            "estadoCitas": estado,
            "mascotas": Mascota.objects.all(),
            "clientes": User.objects.select_related("cliente"),
            "veterinarios": User.objects.select_related("veterinario")
        }

        return render(request, "frmruta_de_tu_template.html", retorno)

    else:
        # Si no es una solicitud POST, simplemente renderiza el formulario inicial con los datos necesarios (por ejemplo, la lista de mascotas, clientes y veterinarios)
        retorno = {
            "mensaje": "",
            "estado": False,
            "mascota": Mascota.objects.all(),
            "cliente": User.objects.all("cliente"),
            "veterinario": User.objects.all("veterinario"),
        }

        return render(request, "frmRegistrarCitaVeterinaria.html", retorno)



def inicioTecnico(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                    "rol": request.user.groups.get().name}
        return render(request, "tecnico/inicio.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})
    
def especialistaSolicitudes(request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user,
                    "rol": request.user.groups.get().name}
        return render(request, "especialista/solicitudes.html", datosSesion)
    else:
        mensaje = "Debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje": mensaje})

