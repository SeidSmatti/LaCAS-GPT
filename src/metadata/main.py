# main.py

from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from subapi_hal import search_hal_api
from subapi_nakala import search_nakala_api
from subapi_zenodo import search_zenodo_api
from subapi_isidore import search_isidore_api
from subapi_arxiv import search_arxiv_api
from subapi_istex import search_istex_api

app = Flask(__name__)

def search_all_apis(query: str) -> Dict[str, Any]:
    """Fonction coordinatrice pour envoyer des requêtes à plusieurs APIs."""
    # SubAPIs principales
    primary_subapis = {
        'HAL': search_hal_api,
        'Nakala': search_nakala_api,
        'Zenodo': search_zenodo_api
    }

    # Autres subAPIs
    other_subapis = {
        'ISIDORE': search_isidore_api,
        'ArXiv': search_arxiv_api,
        'ISTEX': search_istex_api
    }

    results = {}

    with ThreadPoolExecutor() as executor:
        future_to_api = {}
        # Soumettre les subAPIs principales
        for api_name, api_func in primary_subapis.items():
            future = executor.submit(api_func, query)
            future_to_api[future] = ('primary', api_name)

        # Soumettre les autres subAPIs
        for api_name, api_func in other_subapis.items():
            future = executor.submit(api_func, query)
            future_to_api[future] = ('other', api_name)

        # Collecter les résultats
        primary_results = {}
        other_results = {}
        for future in as_completed(future_to_api):
            group, api_name = future_to_api[future]
            try:
                result = future.result()
                if isinstance(result, list):
                    if group == 'primary':
                        primary_results[api_name] = result
                    else:
                        other_results[api_name] = result
                else:
                    error_message = [result]
                    if group == 'primary':
                        primary_results[api_name] = error_message
                    else:
                        other_results[api_name] = error_message
            except Exception as exc:
                error_message = [f"Erreur : {exc}"]
                if group == 'primary':
                    primary_results[api_name] = error_message
                else:
                    other_results[api_name] = error_message

    # Combiner les résultats
    results.update(primary_results)
    results['Others'] = other_results

    return results

@app.route('/search', methods=['GET'])
def search():
    """Route Flask pour gérer les requêtes GET des recherches."""
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Veuillez fournir un paramètre de requête"}), 400

    results = search_all_apis(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

