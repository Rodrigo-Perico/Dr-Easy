import nltk
import string
import heapq
from transformers import T5Tokenizer, T5ForConditionalGeneration


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


def summerIA(texto):

    model = T5ForConditionalGeneration.from_pretrained("google-t5/t5-small")
    tokenizer = T5Tokenizer.from_pretrained("google-t5/t5-small")

    preprocessor_input = "summarize: " + texto
    tokens_input = tokenizer.encode(preprocessor_input, return_tensors="pt", max_length=1024, truncation=True)

    summary_ids = model.generate(tokens_input,
                                 min_length=100,
                                 max_length=510,
                                 length_penalty=4.0)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary