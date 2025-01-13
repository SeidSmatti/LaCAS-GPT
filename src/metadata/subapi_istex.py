# subapi_istex.py

import requests
from typing import List, Dict, Union

def search_istex_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API ISTEX avec la requête donnée."""
    url = "https://api.istex.fr/document/"
    params = {
        'q': query,  # La requête de recherche
        'size': 5  # Nombre maximum de résultats retournés
    }

    try:
        # Effectuer une requête GET à l'API ISTEX
        response = requests.get(url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()
        results = []

        hits = data.get('hits', [])  # Récupérer les résultats (hits) de la réponse
        for hit in hits:
            metadata = hit.get('metadata', {})  # Récupérer les métadonnées de chaque résultat
            results.append({
                'Title': metadata.get('title', 'N/A'),  # Titre du document
                'Abstract': metadata.get('abstract', 'N/A'),  # Résumé du document
                'Submitted Date': metadata.get('publicationDate', 'N/A'),  # Date de publication
                'Document Type': metadata.get('genre', 'N/A'),  # Genre ou type de document
                'URI': f"https://api.istex.fr/document/{hit.get('id', '')}"  # Lien vers le document
            })

        return results
    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "climate change"  # Exemple de requête
    results = search_istex_api(query)
    for result in results:
        print(result)

