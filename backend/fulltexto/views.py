from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView
from .models import Fulltexto
from docx import Document
import nltk
import string
import heapq
import io

# Função de pré-processamento
def preprocessamento(texto):
    stopwords = nltk.corpus.stopwords.words('portuguese')
    pontuacoes = string.punctuation

    if isinstance(texto, bytes):  # Verifica se o texto é do tipo bytes
        # Transforma o conteúdo do arquivo em texto formatado
        texto = texto.decode('utf-8')

    # Tokenização e remoção de stopwords e pontuações
    tokens = nltk.word_tokenize(texto)
    tokens = [palavra for palavra in tokens if palavra not in stopwords and palavra not in pontuacoes]

    # Junta os tokens em um texto formatado
    texto_formatado = ' '.join(tokens)

    return texto_formatado

# Função para extrair as melhores frases
def extrair_melhores_frases(texto_clean, texto_formatado, n=10):

    frequencia_palavras = nltk.FreqDist(nltk.word_tokenize(texto_formatado))
    frequencia_maxima = max(frequencia_palavras.values())
    for palavra in frequencia_palavras:
        frequencia_palavras[palavra] = (frequencia_palavras[palavra] / frequencia_maxima)

    #separo por pontos/cada frase

    lista_frases = nltk.sent_tokenize(texto_clean)
    nota_frases = {}
    for frase in lista_frases:
        for palavra in nltk.word_tokenize(frase.lower()):
            if palavra in frequencia_palavras:
                if frase not in nota_frases:
                    nota_frases[frase] = frequencia_palavras[palavra]
                else:
                    nota_frases[frase] += frequencia_palavras[palavra]

    melhores_frases = heapq.nlargest(n, nota_frases, key=nota_frases.get)
    return melhores_frases

class Homeresposta(TemplateView):
    template_name = "homeresposta.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obter o último objeto Fulltexto salvo no banco de dados
        fulltexto = Fulltexto.objects.last()
        if fulltexto:
            context['texto_original'] = fulltexto.file.read().decode('utf-8')
            context['texto_formatado'] = fulltexto.texto_atualizado
        return context
class Homepageupload(TemplateView):
    template_name = "homeupload.html"

    def post(self, request, *args, **kwargs):
        if 'file' in request.FILES:  # Verifica se um arquivo foi enviado
            uploaded_file = request.FILES['file']  # Obtém o arquivo do formulário
            texto_clean = uploaded_file.read().decode('utf-8')

            # Pré-processamento do texto
            texto_formatado = preprocessamento(texto_clean)

            # Extração das melhores frases
            melhores_frases = extrair_melhores_frases(texto_clean, texto_formatado)

            # Salvando o texto original no campo 'file' do modelo Fulltexto
            fulltexto = Fulltexto()
            fulltexto.file.save(uploaded_file.name, uploaded_file)

            # Salvando as melhores frases no campo 'texto_atualizado' do modelo Fulltexto
            fulltexto.texto_atualizado = '\n'.join(melhores_frases)

            fulltexto.save()

            return redirect('resposta')  # Redireciona para a página de sucesso
        else:
            # Se nenhum arquivo foi enviado, renderiza novamente a página inicial com uma mensagem de erro
            return render(request, self.template_name, {'error_message': 'Nenhum arquivo enviado.'}) + render(request, self.template_name, {'error_message': 'Nenhum arquivo enviado.'})

class Upload_success(TemplateView):
    template_name = 'upload_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obter o último objeto Fulltexto salvo no banco de dados
        fulltexto = Fulltexto.objects.last()
        if fulltexto:
            context['texto_original'] = fulltexto.file.read().decode('utf-8')
            context['texto_formatado'] = fulltexto.texto_atualizado
        return context