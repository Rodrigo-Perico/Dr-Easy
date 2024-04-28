from django.db import models

# Create your models here.

class Fulltexto(models.Model):
    file = models.FileField(upload_to='textos/')
    texto_atualizado = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

#salva nessa mesma base o resumo , e mostro na view
#trata o input
#salva bd
#chama metodo de resumo
#e texto saido texto resumido
#resultada salva no bd
#mostra view - retorna o resumo , retorna se o resto funcionou,