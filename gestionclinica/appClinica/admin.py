from django.contrib import admin
from appClinica.models import *
# Register your models here.

from django.contrib.auth import get_user_model

User = get_user_model()
admin.site.register(User)
admin.site.register(Mascota)
admin.site.register(ExamenClinico)
admin.site.register(HistoriaClinica)
admin.site.register(CitaVeterinaria)
admin.site.register(TipoRemision)
admin.site.register(ElementoSubTipoRemision)
admin.site.register(Remision)
admin.site.register(Servicios)
admin.site.register(AgendarCita)