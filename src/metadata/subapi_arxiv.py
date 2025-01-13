# subapi_arxiv.py

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Union

def search_arxiv_api(query: str) -> Union[List[Dict[str, str]], str]:
    """Rechercher dans l'API arXiv avec la requête donnée."""
    url = 'http://export.arxiv.org/api/query'

    # Construire le paramètre search_query
    search_query = '+'.join(query.strip().split())

    params = {
        'search_query': f'all:{search_query}',  # Rechercher dans tous les champs
        'start': 0,  # Point de départ des résultats
        'max_results': 5  # Nombre maximum de résultats retournés
    }

    try:
        # Effectuer une requête GET à l'API arXiv
        response = requests.get(url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        content = response.content

        # Analyser la réponse XML
        root = ET.fromstring(content)
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',  # Espace de noms pour les éléments Atom
            'arxiv': 'http://arxiv.org/schemas/atom'  # Espace de noms pour les éléments spécifiques à arXiv
        }

        entries = root.findall('atom:entry', ns)  # Trouver toutes les entrées (articles)
        results = []

        for entry in entries:
            # Extraire le titre
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None else 'N/A'

            # Extraire le résumé (abstract)
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip() if summary_elem is not None else 'N/A'

            # Extraire la date de soumission
            published_elem = entry.find('atom:published', ns)
            submitted_date = published_elem.text.strip() if published_elem is not None else 'N/A'

            # Extraire les auteurs
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            authors_str = ', '.join(authors) if authors else 'N/A'

            # Le type de document est défini par défaut sur 'Article'
            document_type = 'Article'

            # Extraire l'URI
            id_elem = entry.find('atom:id', ns)
            uri = id_elem.text.strip() if id_elem is not None else 'N/A'

            results.append({
                'Title': title,  # Titre de l'article
                'Abstract': abstract,  # Résumé
                'Submitted Date': submitted_date,  # Date de soumission
                'Document Type': document_type,  # Type de document
                'Authors': authors_str,  # Liste des auteurs
                'URI': uri  # Lien vers l'article
            })

        return results

    except requests.RequestException as e:
        # Retourner un message d'erreur en cas d'exception liée à la requête
        return f"Erreur : {e}"
    except (ET.ParseError, AttributeError) as e:
        # Retourner un message d'erreur en cas de problème lors de l'analyse XML
        return f"Erreur d'analyse : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "Climate change"  # Exemple de requête
    results = search_arxiv_api(query)
    for result in results:
        print(result)

