# subapi_zenodo.py

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Union

def search_zenodo_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API Zenodo avec la requête donnée."""
    url = 'https://zenodo.org/api/records'
    params = {
        'q': query,  # La requête de recherche
        'sort': 'bestmatch',  # Trier les résultats par pertinence
        'page': 1,  # Numéro de page
        'size': 10  # Nombre maximum de résultats par page
    }

    try:
        # Effectuer une requête GET à l'API Zenodo
        response = requests.get(url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()
        records = data.get('hits', {}).get('hits', [])
        results = []

        for record in records:
            metadata = record.get('metadata', {})
            raw_description = metadata.get('description', '')  # Description brute
            if raw_description:
                # Nettoyer le HTML présent dans la description avec BeautifulSoup
                soup = BeautifulSoup(raw_description, 'html.parser')
                abstract = soup.get_text(separator=' ', strip=True)
            else:
                abstract = 'N/A'

            results.append({
                'Title': metadata.get('title', 'N/A'),  # Titre
                'Abstract': abstract,  # Résumé
                'Submitted Date': record.get('created', 'N/A'),  # Date de soumission
                'Document Type': metadata.get('resource_type', {}).get('title', 'N/A').upper(),  # Type de document
                'URI': record.get('links', {}).get('doi', record.get('links', {}).get('self', 'N/A'))  # Lien DOI ou lien direct
            })

        return results
    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "climate change"  # Exemple de requête
    results = search_zenodo_api(query)
    for result in results:
        print(result)

