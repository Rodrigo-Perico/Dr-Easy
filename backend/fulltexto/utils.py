import nltk
import string
import heapq
from transformers import T5Tokenizer, T5ForConditionalGeneration
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF para PDF
from docx import Document  # python-docx para DOCX
import os
import chardet
from langchain_community.document_loaders import Docx2txtLoader
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.uploadedfile import TemporaryUploadedFile
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader

##############Pegar String#########################
#def extrair_texto_pdf(file):


def extrair_texto_pdf(file):
    # Salva o arquivo temporariamente em disco
    with NamedTemporaryFile(delete=False) as tmp_file:
        for chunk in file.chunks():
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name
    loader = PyPDFLoader(tmp_file_path)
    pages = loader.load_and_split()
    texto = ""
    for i in range(len(pages) - 1):
        texto += pages[i + 1].page_content
    return texto
def extrair_texto_docx(file):
    # Salva o arquivo temporariamente em disco
    with NamedTemporaryFile(delete=False) as tmp_file:
        for chunk in file.chunks():
            tmp_file.write(chunk)
        tmp_file_path = tmp_file.name

    # Cria uma instância da classe Docx2txtLoader com o conteúdo do arquivo
    #loader = Docx2txtLoader(file)

    # Carrega o arquivo e extrai o texto
    #data = loader.load()
    #texto = data[0].page_content
    loader = UnstructuredWordDocumentLoader(tmp_file_path)
    data = loader.load()
    texto = data[0].page_content

    return texto


def extrair_texto_txt(file):
    # Extrair texto de arquivos TXT
    with file.open('rb') as f:
        file_content = f.read()
        # Detectar a codificação usando chardet
        encoding = chardet.detect(file_content)['encoding']
        if encoding is None:
            # Se a codificação não for detectada, usar UTF-8 como padrão
            encoding = 'utf-8'
        # Decodificar o arquivo com a codificação detectada
        texto = file_content.decode(encoding, errors='ignore')
    return texto

###################################################
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

    # Verificar se o dicionário de frequências está vazio
    if not frequencia_palavras:
        return []

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

##############################MODELO T5####################################################################3

'''
def summerIA(texto):

    model = T5ForConditionalGeneration.from_pretrained("google-t5/t5-small")
    tokenizer = T5Tokenizer.from_pretrained("google-t5/t5-small")

    preprocessor_input = "summarize: " + texto
    tokens_input = tokenizer.encode(preprocessor_input, return_tensors="pt", max_length=1024, truncation=True)

    summary_ids = model.generate(tokens_input,
                                 min_length=150,
                                 max_length=750,
                                 length_penalty=1.5,
                                 num_beams=4,
                                 early_stopping=True,# Impedir que a geração pare assim que o modelo tiver decidido sua saída
                                 no_repeat_ngram_size=3,  # Evitar a repetição de trigramas
                                 )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary
'''
'''
def summerIA(texto):
    model = T5ForConditionalGeneration.from_pretrained("T5-small")
    tokenizer = T5Tokenizer.from_pretrained("T5-small")

    # Dividir o texto em partes menores
    partes_texto = [texto[i:i+400] for i in range(0, len(texto), 400)]

    resumos = []
    for parte in partes_texto:
        preprocessor_input = "summarize: " + parte
        tokens_input = tokenizer.encode(preprocessor_input, return_tensors="pt", max_length=1024, truncation=True)

        summary_ids = model.generate(tokens_input,
                                      min_length=50,
                                      max_length=150,
                                      length_penalty=2.0,
                                      num_beams=4)

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        resumos.append(summary)

    return " ".join(resumos)
'''
def summerIA(texto):
    # Carregar o modelo e o tokenizador T5
    model = T5ForConditionalGeneration.from_pretrained("T5-small")
    tokenizer = T5Tokenizer.from_pretrained("T5-small", legacy= False)

    # Criar um TextSplitter para dividir o texto em partes menores
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Definir o tamanho máximo de cada parte (chave correta)
        chunk_overlap=50,  # Definir a sobreposição para manter o contexto entre as partes
        separators=["\n", ".", "!", "?"]  # Caracteres para dividir o texto
    )

    # Dividir o texto em partes menores
    partes_texto = text_splitter.split_text(texto)

    # Lista para armazenar os resumos de cada parte
    resumos = []

    # Resumir cada parte do texto usando o modelo T5
    for parte in partes_texto:
        # Preparar a entrada para o modelo T5
        preprocessor_input = "summarize: " + parte
        tokens_input = tokenizer.encode(preprocessor_input, return_tensors="pt", max_length=1024, truncation=True)

        # Gerar o resumo usando o modelo T5
        summary_ids = model.generate(tokens_input,
                                     min_length=30,
                                     max_length=150,
                                     length_penalty=2.0,
                                     num_beams=4)

        # Decodificar o resumo gerado
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Adicionar o resumo à lista de resumos
        resumos.append(summary)

    # Juntar todos os resumos em um único resumo
    resumo_final = " ".join(resumos)

    return resumo_final