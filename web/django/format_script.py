import os
import bs4
from bs4 import BeautifulSoup
import re

def format_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    formatter = bs4.formatter.HTMLFormatter()
    formatted_html = soup.prettify(formatter=formatter)
    return re.sub(r'\s*</path>',r'</path>', formatted_html)

def reformat_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    formatted_html = format_html(html_content)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(formatted_html)

def reformat_html_in_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            print(file)
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                reformat_html_file(file_path)


# Reformatte le fichier spécifié
file_path = 'templates/home2.html'
reformat_html_file(file_path)


# Reformatte tous les fichiers dans le dossier spécifié
# directory_path = 'templates'
# reformat_html_in_directory(directory_path)

#Change space size to 1 -> convert to tab -> change tab size to 4