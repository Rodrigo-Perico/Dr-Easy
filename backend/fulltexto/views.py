from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from .models import Fulltexto, Textoatualizado
from langchain_community.document_loaders import TextLoader
from .utils import preprocessamento, extrair_melhores_frases, summerIA, extrair_texto_docx, extrair_texto_txt,extrair_texto_pdf
import chardet
import fitz  # PyMuPDF para PDF
from docx import Document  # python-docx para DOCX
import os
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

            #ver a extencao
            file_extension = os.path.splitext(uploaded_file.name)[-1].lower()

            # Inicializa a variável texto
            texto = ""

            # Leitura e processamento do arquivo de acordo com a extensão
            if file_extension == ".pdf":
                texto = extrair_texto_pdf(uploaded_file)
            elif file_extension == ".docx":
                texto = extrair_texto_docx(uploaded_file)
            elif file_extension == ".txt":
                texto = extrair_texto_txt(uploaded_file)

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


