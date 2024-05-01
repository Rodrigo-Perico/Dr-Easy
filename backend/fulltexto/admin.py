from django.contrib import admin
from .models import Fulltexto,Textoatualizado, Usuario
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Fulltexto)
admin.site.register(Textoatualizado)
admin.site.register(Usuario,UserAdmin) #classe que vai gerenciar os usuarios