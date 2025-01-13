# fetcher.py

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from io import BytesIO
import PyPDF2

def fetch_and_extract_text(url):
    # Identifier le dépôt en fonction de l'URL
    if 'hal' in url:
        pdf_url = fetch_hal_pdf_url(url)
    elif 'zenodo' in url:
        pdf_url = fetch_zenodo_pdf_url(url)
    elif 'nakala' in url or 'nkl.' in url:
        pdf_url = fetch_nakala_pdf_url(url)
    else:
        raise Exception("Dépôt non pris en charge ou URL invalide.")
    
    # Télécharger le PDF
    response = requests.get(pdf_url)
    response.raise_for_status()
    pdf_bytes = BytesIO(response.content)
    
    # Extraire le texte du PDF
    text = extract_text_from_pdf(pdf_bytes)
    return text

def fetch_hal_pdf_url(url):
    # Ajouter '/document' à l'URL
    if not url.endswith('/'):
        url += '/'
    pdf_url = url + 'document'
    return pdf_url

def fetch_zenodo_pdf_url(url):
    # Récupérer la page et l'analyser pour trouver le lien du PDF
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trouver la balise <a> correspondant à vos critères
    # <a role="button" class="ui compact mini button" href="...">Download</a>
    download_links = soup.find_all('a', {'role': 'button', 'class': 'ui compact mini button'})
    for link in download_links:
        link_text = link.get_text(strip=True)
        if link_text.lower() == 'download':
            href = link.get('href')
            if not href:
                continue
            # Construire l'URL complète du PDF
            pdf_url = urljoin('https://zenodo.org', href)
            return pdf_url
    raise Exception("Lien de téléchargement introuvable sur la page Zenodo.")

def fetch_nakala_pdf_url(url):
    # Récupérer la page et l'analyser pour trouver l'attribut data-clipboard-text
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trouver le bouton avec l'attribut data-clipboard-text et un texte spécifique
    # <button data-clipboard-text="...">...Copier l'url de téléchargement</button>
    download_buttons = soup.find_all('button', {'data-clipboard-text': True})
    for button in download_buttons:
        button_text = button.get_text(strip=True)
        if "Copier l'url de téléchargement" in button_text:
            pdf_url = button['data-clipboard-text']
            return pdf_url
    raise Exception("Lien de téléchargement introuvable sur la page Nakala.")

def extract_text_from_pdf(pdf_bytes):
    try:
        reader = PyPDF2.PdfReader(pdf_bytes)
        extracted_text = ""
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                text = text.strip()
                # Inclure le numéro de page dans le texte extrait
                extracted_text += f"Page {page_num}:\n{text}\n\n"
        extracted_text = extracted_text.strip()
        return extracted_text
    except Exception as e:
        raise Exception(f"Erreur lors du traitement du PDF : {e}")

