import os
import re
import zipfile


project_root = os.path.dirname(os.path.abspath(__file__))

twenty_n_path = os.path.join(project_root, 'data', '20news-18828', '20news-18828')
bac_path = os.path.join(project_root, 'data', 'BAC', 'blogs.zip')
consolidated_news_path = os.path.join(project_root, 'consolidated_twenty_news.txt')

twenty_n_regex = r'''
^From:.*?\n|                      # Ignora la línea que empieza con 'From:' y lo que sigue hasta el final de la línea
^Subject:.*?\n|                   # Ignora la línea que empieza con 'Subject:' y lo que sigue hasta el final de la línea
^Archive-name:.*?\n|              # Ignora la línea que empieza con 'Archive-name:' y lo que sigue hasta el final de la línea
^Alt-atheism-archive-name:.*?\n|  # Ignora la línea que empieza con 'Alt-atheism-archive-name:' y lo que sigue hasta el final de la línea
^Last-modified:.*?\n|             # Ignora la línea que empieza con 'Last-modified:' y lo que sigue hasta el final de la línea
^Version:.*?\n|                   # Ignora la línea que empieza con 'Version:' y lo que sigue hasta el final de la línea
^.*@.*?\n|                        # Ignora la línea que contiene '@' y lo que sigue hasta el final de la línea
In\sarticle.*?writes:\n|          # Ignora todo lo que está entre 'In article...' y 'writes:'
[^a-zA-Z0-9\s.,]                  # Elimina cualquier carácter que no sea una letra, un número o un espacio
|^>+                              # Elimina '>' al inicio de una línea
|\s*>+                            # Elimina '>' seguido por espacios
^-+$                              # Ignora las líneas que contienen solo '-'
^=+$                              # Ignora las líneas que contienen solo '='
'''

def list_directories(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

def list_files(path):
    return [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

def get_relevant_text_twenty_news(path: str) -> str:
    global twenty_n_regex
    with open(path, 'r') as file:
        text = file.read()
        cleaned_text = re.sub(twenty_n_regex, '', text, flags=re.VERBOSE | re.MULTILINE)
    return cleaned_text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace('  ', ' ').replace('   ', ' ')

def get_relevant_text_bac(content: str) -> str:
    dates = re.findall(r'<date>(.*?)</date>', content, re.DOTALL)
    posts = re.findall(r'<post>(.*?)</post>', content, re.DOTALL)
    
    posts = [re.sub(r'\s+', ' ', post).strip().replace('urlLink', '').replace('  ', ' ') for post in posts]
    
    return list(zip(dates, posts))

def process_twenty_news_data(path: str) -> None:
    with open('consolidated_news.txt', 'w', encoding='utf-8') as output_file:
        news_dirs = list_directories(path)
        
        for each_news_dir in news_dirs:
            each_path = os.path.join(path, each_news_dir)
            news_files = list_files(each_path)
            
            for each_news_file in news_files:
                file_path = os.path.join(each_path, each_news_file)
                text = get_relevant_text_twenty_news(file_path)
                output_file.write(text + '\n')

def process_bac_data(zip_path: str) -> None:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_names = zip_ref.namelist()
        
        with open('consolidated_bac.txt', 'w', encoding='utf-8') as output_file:
            for file_name in file_names:
                if not file_name.endswith('/'):
                    with zip_ref.open(file_name) as file:
                        try:
                            content = file.read().decode('utf-8')
                        except UnicodeDecodeError:
                            # if utf-8 fails, use latin1
                            content = file.read().decode('latin1')
                        
                        data_pairs = get_relevant_text_bac(content)
                        
                        for date, post in data_pairs:
                            output_file.write(f"{date} - {post}\n")

if __name__ == '__main__':
    process_twenty_news_data(twenty_n_path)
    process_bac_data(bac_path)
    