#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import ollama
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import requests  # Solo para scraping web, no para Ollama
import time
import re

load_dotenv()

MODEL = os.getenv("MODEL", "llama3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MAX_DEPTH = int(os.getenv("MAX_DEPTH", 4))
TIMEOUT = int(os.getenv("TIMEOUT", 10))

def ensure_https(url):
    if url.startswith('http://'):
        return 'https://' + url[len('http://'):]
    elif not url.startswith('http'):
        return 'https://' + url
    return url

def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}")

def extract_text_from_pdf(url):
    import pdfplumber
    import requests
    from io import BytesIO
    try:
        response = requests.get(url, timeout=TIMEOUT)
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)
    except Exception as e:
        log_error(f"No se pudo extraer texto del PDF {url}: {e}")
        return ""

def extract_text_from_docx(url):
    import requests
    from io import BytesIO
    from docx import Document
    try:
        response = requests.get(url, timeout=TIMEOUT)
        doc = Document(BytesIO(response.content))
        return '\n'.join([p.text for p in doc.paragraphs])
    except Exception as e:
        log_error(f"No se pudo extraer texto del DOCX {url}: {e}")
        return ""

def scrape_recursive(url, visited=None, depth=0, regex=None, max_results=None, results=None, texts=None):
    url = ensure_https(url)
    if visited is None:
        visited = set()
    if results is None:
        results = []
    if texts is None:
        texts = []
    if url in visited or (max_results and len(results) >= max_results):
        return ""
    visited.add(url)
    log_info(f"Nivel {depth+1} - Scrapeando: {url}")
    try:
        if url.lower().endswith('.pdf'):
            text = extract_text_from_pdf(url)
        elif url.lower().endswith('.docx'):
            text = extract_text_from_docx(url)
        else:
            response = requests.get(url, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all(['p', 'li', 'span', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
        texts.append(text)
        # Lógica para el resumen según regex
        if regex:
            matches = re.findall(regex, text, re.IGNORECASE)
            if matches:
                resumen = ask_ollama(text)
                resumen_header = f"\n{'='*80}\n[RESUMEN OLLAMA]\nURL: {url}\n{'='*80}"
                print(f"{resumen_header}\n{resumen}\n{'='*80}\n")
        else:
            resumen = ask_ollama(text)
            resumen_header = f"\n{'='*80}\n[RESUMEN OLLAMA]\nURL: {url}\n{'='*80}"
            print(f"{resumen_header}\n{resumen}\n{'='*80}\n")
        # Solo buscar enlaces en HTML
        if not (url.lower().endswith('.pdf') or url.lower().endswith('.docx')):
            base = urlparse(url).netloc
            links = set()
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                link = ensure_https(link)
                if urlparse(link).netloc == base and link not in visited:
                    links.add(link)
            for link in links:
                if max_results and len(results) >= max_results:
                    break
                time.sleep(0.2)
                scrape_recursive(link, visited, depth+1, regex, max_results, results, texts)
        return '\n'.join(results) if regex else '\n'.join(texts)
    except Exception as e:
        log_error(f"No se pudo acceder a {url}: {e}")
        return ""

def ask_ollama(text, model=MODEL):
    prompt = (
        "Haz un breve resumen del siguiente contenido extraído de una página web. No busques ni menciones contactos, emails ni teléfonos.\n\nContenido extraído: " + text
    )
    response = ollama.generate(model=model, prompt=prompt)
    return response.get("response", "No response from Ollama")

def scrape_url(url, regex=None, max_depth=MAX_DEPTH, max_results=None):
    url = ensure_https(url)
    return scrape_recursive(url, max_depth=max_depth, regex=regex, max_results=max_results)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python scrapper_ollama.py <URL> [regex]")
        sys.exit(1)
    url = ensure_https(sys.argv[1])
    regex = sys.argv[2] if len(sys.argv) > 2 else None
    if regex:
        try:
            re.compile(regex)
        except re.error as e:
            log_error(f"El regex proporcionado no es válido: {e}")
            sys.exit(1)
    print(f"Scrapeando {url} ...")
    scrape_recursive(url, regex=regex)
