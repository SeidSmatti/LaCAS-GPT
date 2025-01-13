# subapi_nakala.py

import requests
from typing import List, Dict, Union

def search_nakala_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API Nakala avec la requête donnée."""
    url = "https://api.nakala.fr/search"
    params = {
        'q': query,  # La requête de recherche
        'fq': '',  # Filtre de requête (vide par défaut)
        'facet': '',  # Facettes de recherche (vide par défaut)
        'order': 'relevance',  # Ordre des résultats par pertinence
        'page': '1',  # Numéro de la page à récupérer
        'size': '10'  # Nombre maximum de résultats par page
    }
    headers = {
        'accept': 'application/json'  # Type de contenu accepté
    }

    try:
        # Effectuer une requête GET à l'API Nakala
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()
        results = []

        # Parcourir les données retournées
        for item in data.get('datas', []):
            # Extraire les métadonnées
            metas = {meta.get('propertyUri'): meta.get('value', '') for meta in item.get('metas', [])}
            results.append({
                'Identifier': item.get('identifier', 'N/A'),  # Identifiant de l'élément
                'Status': item.get('status', 'N/A'),  # Statut de l'élément
                'Creation Date': item.get('creDate', 'N/A'),  # Date de création
                'Title': metas.get('http://nakala.fr/terms#title', 'N/A'),  # Titre
                'Description': metas.get('http://purl.org/dc/terms/description', 'N/A')  # Description
            })

        return results
    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "climate change"  # Exemple de requête
    results = search_nakala_api(query)
    for result in results:
        print(result)

