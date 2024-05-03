from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Fulltexto, Textoatualizado
from .utils import preprocessamento, extrair_melhores_frases, summerIA
import chardet
# Create your views here.

class Homeresposta(TemplateView):
    template_name = 'homeresposta.html'

    def get_context_data(self, **kwargs):
        # Obter o contexto da classe pai
        context = super().get_context_data(**kwargs)

        # Obter o ID do objeto Fulltexto passado na URL
        fulltexto_id = kwargs.get('id')

        # Filtrar o Textoatualizado com base no fulltexto_id
        texto_atualizado_queryset = Textoatualizado.objects.filter(fulltexto=fulltexto_id)

        # Se o queryset não estiver vazio, pegue o primeiro objeto
        if texto_atualizado_queryset.exists():

            #texto_atualizado_obj = texto_atualizado_queryset.first()
            #context['texto_atualizado'] = texto_atualizado_obj.texto_atualizado
            context['texto_atualizado'] = texto_atualizado_queryset
        else:
            context['texto_atualizado'] = None

        return context
class Homepageupload(TemplateView):
    template_name = "homeupload.html"

    def post(self, request, *args, **kwargs):
        if 'file' in request.FILES:
            # Obtém o arquivo do formulário
            uploaded_file = request.FILES['file']

            # Cria uma instância do modelo Fulltexto
            fulltexto = Fulltexto()

            # Salva o arquivo no campo 'file' do modelo Fulltexto
            fulltexto.file.save(uploaded_file.name, uploaded_file)

            # Leitura e processamento do arquivo
            with uploaded_file.open('rb') as file:
                file_content = file.read()
                # Detectar a codificação usando chardet
                encoding = chardet.detect(file_content)['encoding']
                if encoding is None:
                    # Se a codificação não for detectada, usar UTF-8 como padrão
                    encoding = 'utf-8'

                # Decodificar o arquivo com a codificação detectada
                texto = file_content.decode(encoding, errors='ignore')

            #salva o texto original
            fulltexto.texto_original = texto

            # Salva o objeto fulltexto no banco de dados
            fulltexto.save()



            if texto:
                ##################### PRIMEIRO MODELO #######################################
                texto_formatado = preprocessamento(texto)
                melhores_frases = extrair_melhores_frases(texto, texto_formatado)

                # Continuar com o código se o texto não for vazio
                texto_atualizado_obj = Textoatualizado()
                # Associa o objeto Fulltexto ao objeto Textoatualizado
                texto_atualizado_obj.fulltexto = fulltexto
                #nome do modelo a ser salvo
                texto_atualizado_obj.modelo = "resumo heuristico"
                # Converte a lista de melhores frases em uma string (separada por nova linha, por exemplo)
                texto_atualizado_obj.texto_atualizado = '\n'.join(melhores_frases)

                # Salva o objeto Textoatualizado no banco de dados
                texto_atualizado_obj.save()

                ##################### MODELO DE IA #######################################
                resumo_IA = summerIA(texto)

                texto_atualiza_IA = Textoatualizado()
                texto_atualiza_IA.fulltexto = fulltexto
                texto_atualiza_IA.modelo = "IA T5"
                texto_atualiza_IA.texto_atualizado = resumo_IA

                texto_atualiza_IA.save()



            # Redireciona para a página inicial (ou outra página de sua escolha)
            return redirect(reverse('uploaded_text', args=[fulltexto.id]))

        # Se nenhum arquivo foi enviado, renderiza a página de upload com uma mensagem de erro
        return render(request, self.template_name, {'error_message': 'Nenhum arquivo enviado.'})

