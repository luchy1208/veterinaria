from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


rol = [
    ('Administrativo',"Administrativo"),('MedicoVeterinario',"MedicoVeterinario"),('AuxiliarVeterinario',"AuxiliarVeterinario"),('Cliente','Cliente'),
]

tipoServicio = [
    ('ServicioBasico',"ServicioBasico"),('ServicioBienestar',"ServicioBienestar"),('Urgencias',"Urgencias"),('OtrosServicios',"OtrosServicios"),
]
            
estadoCita=[
    ('Pendiente',"Pendiente"),('Atendida',"Atendida"),('Cancelada',"Cancelada"),
]
tipoUsuario=[
    ('Administrador','Administrador'),('Veterinario','Veterinario'),('Auxiliar','Auxiliar'),('Cliente','Cliente'),
]
sexoMascota = [
    ('Hembra',"Hembra"),('Macho',"Macho"),
]
especie = [
    ('Canino',"Canino"),('Felino',"Felino"),('Reptil',"Reptil"),('Roedor',"Roedor"),('Ave',"Ave"),('Pez',"Pez"),('Otro',"Otro"),
]
tamañoMascota= [
    ('P',"Pequeño"),('M',"Mediano"),('G',"Grande"),('EG',"Extragrande"),
]
longitudPelo=[
    ('SinPelo',"Sin Pelo"),('Pelo Corto',"Pelo Corto"),('Pelo Largo',"Pelo Largo"),('Pelo Crespo',"PeloCrespo"),('Pelo Liso',"Pelo liso"),
]

dietaMascota =[
    ('Concentrado',"Concentrado"),('DietaBARF',"DietaBARF"),('DietaBlanda',"DietaBlanda"),('ComidaCasera',"ComidaCasera"),('Otra',"Otra"),
]
tipoDocumento = [
    ('Cedula Ciudadania',"Cedula ciudadania"),('Cedula Extrangera',"Cedula Extrangera"),
]


class User(AbstractUser):
    userFoto = models.FileField(upload_to=f"fotos/", null=True, blank=True,db_comment="Foto del Usuario")
    userTipo = models.CharField(max_length=18,choices=tipoUsuario,db_comment="Nombre Tipo de usuario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self):
        return f"{self.username}"

class Mascota(models.Model):
    masCodigo = models.CharField(max_length=15, unique=True,db_comment="Código único asignado a la mascota")    
    masCliUsuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                db_comment="usuario #que lleva la mascota ahh la consulta veterinaria")
    masNombre = models.CharField(max_length=50,db_comment="Nombre de la mascota")    
    masEspecie = models.CharField(max_length=7,choices=especie,db_comment="Tipo de mascota")
    masRaza = models.CharField(max_length=15,db_comment="Raza de la mascota")    
    masColor = models.CharField(max_length=15,db_comment="Color de la mascota")    
    masSexo = models.CharField(max_length=7,choices=sexoMascota,db_comment="sexo de la mascota")
    masFechaNacimiento = models.DateField(db_comment="Fecha de nacimiento de la mascota")
    masFoto = models.FileField(upload_to=f"fotos/", null=True, blank=True,db_comment="Foto de la mascota")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro de la mascota")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización de la mascota")

    def __str__(self)->str:
        return f"{self.masCodigo}-{self.masNombre}-{self.masCliUsuario}"

class ExamenClinico(models.Model):
    exaCliTemperatura = models.SmallIntegerField(db_comment="T° corporal: 35,36,37..")    
    exaClifreCardiaca = models.SmallIntegerField(null=True,db_comment="Frecuencia cardiaca:..")
    exaCliFreRespiratoria = models.SmallIntegerField(null=True,db_comment="Frecuencia Respiratoria:..")
    exaCliPulso = models.SmallIntegerField(null=True,db_comment="numero de pulsaciones por minuto:..")
    exaCliEstConciencia = models.CharField(max_length=50,db_comment="describir el estado de conciencia de la mascota") 
    exaCliTemperamento =  models.CharField(max_length=25,db_comment="Temperamento de la mascota") 
    exaCliSisDermatológico = models.TextField(null=True,db_comment="descripcion del sistema Dermatológico")
    exaCliSisRespiratorio = models.TextField(null=True,db_comment="descripcion del sistema Respiratorio")
    exaCliSisCardiovascular = models.TextField(null=True,db_comment="descripcion del sistema Cardiovascular")
    exaCliSisDigestivo = models.TextField(null=True,db_comment="descripcion del sistema Digestivo")
    exaCliSisUrinario = models.TextField(null=True,db_comment="descripcion del sistema Urinario")
    exaCliSisReproductor = models.TextField(null=True,db_comment="descripcion del sistema Reproductor")
    exaCliSisLocomotor= models.TextField(null=True,db_comment="descripcion del sistema Locomotor")
    exaCliOftalmológico = models.TextField(null=True,db_comment="descripcion del examen clinico Oftalmológico")
    exaCliOtológico = models.TextField(null=True,db_comment="descripcion del examen clinico Otológico")
    exaCliNeurológico = models.TextField(null=True,db_comment="descripcion del examen clinico Neurológico")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro de la mascota")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización de la mascota")
    
    def __str__(self)->str:
        return f"{self.exaCliTemperatura}-{self.exaCliFreRespiratoria}-{self.exaCliFreRespiratoria}-{self.exaCliPulso}-{self.exaCliEstConciencia}-{self.exaCliTemperamento}"


class HistoriaClinica(models.Model):
    hisCliCodigo = models.IntegerField(unique=True, db_comment="codigo de Historia Clinica")
    hisCliAcompanante= models.CharField(max_length=100,db_comment="Nombre de la persona que ingresa con la mascota")
    hisCliVetUsuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,
                                        db_comment="Hace referencia a usuario")
    hisCliMascota = models.ForeignKey(Mascota, on_delete=models.PROTECT,db_comment="Informacion de la mascota")
    hisCliMotConsulta = models.TextField(null=True,db_comment="detalladamente se escribe el motivo porque se lleva la mascota a consulta")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de creacion de la Historia Clinica")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización de la mascota")
    hisCliUltCelo = models.DateField(db_comment="Hace referencia a la fecha del ultimo celo de la mascota")
    hisCliNumPartos = models.CharField(max_length=15,unique=True,db_comment="Numero de partos de la mascota")    
    #hisCliVacunacionVigente = models.BooleanField(db_comment="Si la mascota tiene o no las vacunas vigentes")
    hisCliUltVacunacion = models.DateField(db_comment="fecha vacunacion")
    hisCliProVacunacion = models.CharField(max_length=25,db_comment="nombre del producto utilizado en la vacunacion")    
    #hisCliDesVigente = models.BooleanField(db_comment="Si la mascota esta o no desparasitada")
    hisCliConParasitos = models.DateField(db_comment="fecha de aplicacion del producto para control de parasitos")
    hisCliProDesparasitar = models.CharField(max_length=25,db_comment="nombre del producto utilizado para desparasitar")    
    #hisCliConEctoparasitos = models.BooleanField(db_comment="si o no control de ectoparasitos")
    #hisCliFechaEctoparasitos = models.DateField(db_comment="Hace referencia a la fecha del ultimo control de ectoparasitos")
    #hisCliProEctoparasitos = models.CharField(max_length=25,db_comment="nombre del producto utilizado para control de ectoparasitos")    
    hisCliDieta = models.CharField(max_length=30,choices=dietaMascota,db_comment="Tipo de dieta")
    hisCliFreDieta = models.CharField(max_length=15,db_comment="La frecuencia con que se alimentala la mascota")    
    hisCliAnamnesicos = models.TextField(null=True,db_comment="En anamnesicos se describe la sintomatologia del animal")
    hisCliEnfAnteriores = models.TextField(null=True,db_comment="enfermedades que ha sufrido la mascota anteriormente")
    hisCliCirPrevias = models.TextField(null=True,db_comment="cirugias realizadas anteriormente")
    hisCliExaClinico = models.ForeignKey(ExamenClinico, on_delete=models.PROTECT,db_comment="Informacion del examen clinico")
    hisCliDiaDiferencial = models.CharField(max_length=100,db_comment="otras enfermedades que haya presentado la mascota")
    hisCliDiaPresuntivo = models.CharField(max_length=50,db_comment="El posible diagnostico presuntivo")
    hisCliEvolucion = models.CharField(max_length=50,db_comment="La evolucion de la mascota o pronostico")
    
    def __str__(self)->str:
        return f"{self.hisCliCodigo}-{self.hisCliMascota}"

class Servicios(models.Model):
    serNombre= models.CharField(max_length=100,db_comment="Nombre del servicio")
    serTipo = models.CharField(max_length=17,choices=tipoServicio,db_comment="tipo de servicio")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.serNombre}-{self.serTipo}"
    
class AgendarCita(models.Model):
    ageCitMascota = models.ForeignKey(Mascota,on_delete=models.PROTECT,db_comment="la mascota")
    ageCitTipServicios = models.ForeignKey(Servicios,on_delete=models.PROTECT,db_comment="Servicios que ofrece la clinica")
    #fechaCitaAgendada = models.DateTimeField(db_comment="Fecha y hora de la cita")
    fechaHoraCita  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de la cita")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.ageCitMascota}-{self.ageCitTipServicios}-{self.fechaHoraCreacion}"
    
class CitaVeterinaria(models.Model):
    citVetCodigo = models.IntegerField(unique=True,db_comment="Codigo de la cita con el veterinario")
    citVetMascota = models.ForeignKey(Mascota,on_delete=models.PROTECT,db_comment="id de la mascota")
    citVetAcompanante= models.CharField(max_length=100,db_comment="Nombre de la persona que ingresa con la mascota")
    citVetAgeCita = models.ForeignKey(AgendarCita, on_delete=models.PROTECT,db_comment="id de la mascota")
    citVetHisClinica = models.ForeignKey(HistoriaClinica,on_delete=models.PROTECT,db_comment="historia Clinica")
    citVetResultadoCita = models.TextField(null=True,db_comment="Resultado de la cita")
    citVetEstado = models.CharField(max_length=10,unique=True,choices=estadoCita,db_comment="Estado de la cita")
    citPrecio= models.IntegerField(db_comment="valor de la consulta medica")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self)->str:
        return f"{self.citVetCodigo}-{self.citVetMascota}-{self.citVetHisClinica}-{self.citVetAgeCita}"

class TipoRemision(models.Model):
    tipoRemNombre = models.CharField(max_length=100,db_comment="Nombre del tipo de remision ej:Examen Laboratorio")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de creacion de la de remision")
    
    def __str__(self)->str:
        return f"{self.tipoRemNombre}"

class ElementoSubTipoRemision(models.Model):
    eleSubTipRemNombre = models.CharField(max_length=100,db_comment="Nombre del subtipo de elemento de la remision ej:Hemograma")
    eleSubTipRemision = models.ForeignKey(TipoRemision, on_delete=models.PROTECT,db_comment="Nombre del tipo de remision")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de creacion de la remision")
    
    def __str__(self)->str:
        return f"{self.eleSubTipRemNombre}-{self.eleSubTipRemision}"

class Remision(models.Model):
    remCodigo = models.IntegerField(unique=True,db_comment="Codigo de la remision")
    remCitVeterinaria= models.ForeignKey(CitaVeterinaria, on_delete=models.PROTECT,db_comment="se trae la citaveterinaria")
    remEleSubTipo = models.ForeignKey(ElementoSubTipoRemision, on_delete=models.PROTECT,db_comment="se trae el elelemnto sub tipo de la remision")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora de creacion de la remision")

    def __str__(self)->str:
        return f"{self.remCodigo}-{self.remCitVeterinaria}-{self.remEleSubTipo}"
    







