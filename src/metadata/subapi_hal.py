# subapi_hal.py

import requests
from typing import List, Dict, Union

def search_hal_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API HAL avec la requête donnée."""
    url = "https://api.archives-ouvertes.fr/search"
    params = {
        'q': query,  # La requête de recherche
        'wt': 'json',  # Format de réponse attendu
        'rows': 10,  # Nombre maximum de résultats retournés
        'fl': 'title_s, abstract_s, submittedDate_tdate, docType_s, uri_s'  # Champs à inclure dans les résultats
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = []

        # Extraire les documents de la réponse
        docs = data.get('response', {}).get('docs', [])
        for doc in docs:
            results.append({
                'Title': doc.get('title_s', ['N/A'])[0] if isinstance(doc.get('title_s'), list) else doc.get('title_s', 'N/A'),
                # Extraire le titre (si c'est une liste, prendre le premier élément)
                'Abstract': doc.get('abstract_s', ['N/A'])[0] if isinstance(doc.get('abstract_s'), list) else doc.get('abstract_s', 'N/A'),
                # Extraire le résumé (si c'est une liste, prendre le premier élément)
                'Submitted Date': doc.get('submittedDate_tdate', 'N/A'),  # Date de soumission
                'Document Type': doc.get('docType_s', 'N/A'),  # Type de document
                'URI': doc.get('uri_s', 'N/A')  # URI pour accéder au document
            })

        return results
    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "climate change"  # Exemple de requête
    results = search_hal_api(query)
    for result in results:
        print(result)

