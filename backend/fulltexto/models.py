from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Fulltexto(models.Model):
    #usuario_id = models.ForeignKey("Usuario",related_name = "Fulltexto", on_delete=models.CASCADE)
    file = models.FileField(upload_to='textos/')
    texto_original = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class Textoatualizado(models.Model):

    fulltexto = models.ForeignKey("Fulltexto",related_name="textoatualizado", on_delete=models.CASCADE)
    modelo = models.TextField(blank=True, null=True)
    texto_atualizado = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class Usuario(AbstractUser):
    pass

#salva nessa mesma base o resumo , e mostro na view
#trata o input
#salva bd
#chama metodo de resumo
#e texto saido texto resumido
#resultada salva no bd
#mostra view - retorna o resumo , retorna se o resto funcionou,