import os, re
import pandas as pd
from typing import List
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET

import nltk
from nltk import PorterStemmer, word_tokenize
from nltk.corpus import stopwords

# Descargar recursos necesarios de NLTK
nltk.download('punkt')  # Tokenizador
nltk.download('stopwords')  # Stopwords

# Configuración de NLTK
nltk.download('punkt_tab')

# %% md
"""
Definimos nuestras funciones de preprocesamiento de tokens y texto. Usamos la librería de `nltk`.
"""

def token_preprocessing(tokens: List[str]) -> List[str]:
    """
    Realiza el preprocesamiento de texto, aplicando las siguientes transformaciones:
    1. Convierte todos los tokens a minúsculas.
    2. Elimina stopwords.
    3. Elimina tokens que no son palabras (puntuación, números, etc.).
    4. Aplica stemming con PorterStemmer.

    Args:
        tokens (List[str]): Lista de tokens a preprocesar.

    Returns:
        List[str]: Lista de tokens preprocesados.
    """
    # Pasa los tokens a minúsculas
    tokens = [word.lower() for word in tokens]

    # Elimina stopwords (asume texto en inglés)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    tokens = [re.sub(r'\W', '', word) for word in tokens]
    tokens = [re.sub(r'\s+[a-zA-Z]\s+', '', word) for word in tokens]
    tokens = [re.sub(r'\^[a-zA-Z]\s+', '', word) for word in tokens]
    tokens = [re.sub(r'[0-9]+', '', word) for word in tokens]

    tokens = [word for word in tokens if len(word) > 0]

    # Aplica stemming
    ps = PorterStemmer()
    return [ps.stem(word) for word in tokens]


def text_preprocessing(text: str) -> List[str]:
    """
    Preprocesa un texto mediante la tokenización y el preprocesamiento de tokens.

    Args:
        text (str): Texto a preprocesar.

    Returns:
        List[str]: Lista de tokens preprocesados.
    """
    # Tokenizar el texto usando el tokenizador de nltk
    tokens = word_tokenize(text)

    # Preprocesar los tokens
    return token_preprocessing(tokens)


# %% md
"""
Definimos una clase `Document`. Esta nos servirá para almacenar cada uno de los documentos en una estructura que nos permita acceder rápidamente al conteo de sus tokens.
"""
class Document:
    def __init__(self, text: str, name: str = 'nameless'):
        """
        Crea un objeto del tipo Document.

        Args:
            text (str): El contenido del documento.
            name (str): El nombre del documento. Por defecto es 'nameless'.
        """
        self.text = text
        self.name = name
        self.tokens = text_preprocessing(text)

        # Preprocesar el texto y contar la frecuencia de cada token
        counter = Counter(self.tokens)

        # Almacenar los conteos de términos como una Serie de pandas
        self.term_counts = pd.Series(counter.values(), index=counter.keys())

    def __repr__(self):
        """
        Representación formal del objeto Document.
        """
        return str(self)

    def __str__(self):
        """
        Representación informal del objeto Document, devuelve el nombre del documento.
        """
        return self.name

    def __iter__(self):
        """
        Iterar sobre los tokens del documento.
        """
        return iter(self.tokens)


# %% md
"""
La siguiente función se encarga de cargar los documentos, parsearlos y convertirlos en objetos de tipo `Document`.
"""
def load_docs(docs_folder_path: Path) -> List[Document]:
    """
    Carga los documentos (con extensión .naf) en una carpeta especificada y crea objetos Document para cada uno.

    Args:
        docs_folder_path (Path): Ruta a la carpeta que contiene los archivos .naf.

    Returns:
        List[Document]: Una lista de objetos Document.
    """
    # Encuentra todos los archivos con extensión .naf en la carpeta especificada
    files = [f for f in os.listdir(docs_folder_path) if f.endswith('.naf')]

    # Lista para almacenar los documentos cargados
    docs = []

    # Procesar cada archivo .naf
    for file in files:
        # Parsea el archivo XML
        tree = ET.parse(os.path.join(docs_folder_path, file))
        root = tree.getroot()

        # Extrae el texto crudo del documento
        raw_text = root.find('.//raw').text

        # Extrae el nombre del archivo, omitiendo la extensión
        name = file.split('.')[1]

        # Crea un objeto Document y lo añade a la lista
        docs.append(Document(raw_text, name))

    return docs