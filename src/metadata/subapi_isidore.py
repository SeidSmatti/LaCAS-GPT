# subapi_isidore.py

import requests
from typing import List, Dict, Union

def search_isidore_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API ISIDORE avec la requête donnée."""
    base_url = "https://api.isidore.science/resource/search"
    
    # Remplacer les espaces par '%2B' pour les requêtes contenant plusieurs mots
    query_encoded = query.replace(' ', '%2B')

    params = {
        'q': query_encoded,  # La requête encodée
        'output': 'json',  # Format de la réponse attendu
        'replies': 5  # Nombre maximum de réponses retournées
    }

    try:
        # Effectuer une requête GET à l'API ISIDORE
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()

        results = []

        # Naviguer dans la structure JSON pour accéder aux réponses
        replies = data.get('response', {}).get('replies', {}).get('content', {}).get('reply', [])
        for reply in replies:
            isidore_data = reply.get('isidore', {})

            # Extraire le titre
            titles = isidore_data.get('title', [])
            title = 'N/A'
            if titles:
                for t in titles:
                    if isinstance(t, dict):  # Si le titre est un dictionnaire
                        title = t.get('$', 'N/A')
                        break
                    elif isinstance(t, str):  # Si le titre est une chaîne
                        title = t
                        break

            # Extraire le résumé (abstract)
            abstract = isidore_data.get('abstract', 'N/A')

            # Extraire la date de soumission
            date = isidore_data.get('date', {}).get('normalizedDate', 'N/A')

            # Extraire le type de document
            types = isidore_data.get('types', {}).get('type', [])
            document_type = types[0] if types else 'N/A'

            # Extraire l'URI
            uri = reply.get('@uri', 'N/A')

            results.append({
                'Title': title,  # Titre du document
                'Abstract': abstract,  # Résumé du document
                'Submitted Date': date,  # Date de soumission
                'Document Type': document_type,  # Type de document
                'URI': uri  # URI du document
            })

        return results

    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"
    except (KeyError, IndexError, TypeError) as e:
        # Retourner un message d'erreur en cas de problème lors de l'analyse des données JSON
        return f"Erreur d'analyse : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "Climate change"  # Exemple de requête
    results = search_isidore_api(query)
    for result in results:
        print(result)

