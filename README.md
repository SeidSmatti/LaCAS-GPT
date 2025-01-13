# LaCAS GPT

## Résumé
La fiabilité des sources d’information représente un défi majeur dans l’utilisation de modèles de langage (LLM) tels que ChatGPT, notamment dans le cadre du projet [LaCAS](https://lacas.inalco.fr/). En effet, ces modèles peuvent générer des contenus inexacts (souvent appelés “hallucinations”), remettant en cause la crédibilité des résultats produits. Pour limiter ce risque, nous avons choisi de réserver l’usage des LLM au formatage et à la gestion des données, plutôt que de les employer comme sources d’information ou intermédiaires entre la source et l’utilisateur.

Ce projet s’articule autour d’un ensemble de scripts Python agissant comme des APIs interrogeant plusieurs dépôts de données (HAL, Nakala, Zenodo, etc.). Les résultats de ces requêtes sont ensuite transmis à un chatbot, qui se charge de coordonner et d’unifier les informations avant de les renvoyer à l’utilisateur. Celui-ci n’interagit donc qu’avec le chatbot, sans avoir à se soucier de la collecte ou de l’agrégation des données en arrière-plan.

## Utilité et fonctionnement
### Utilité

Le projet vise à fournir un point d’accès unique à plusieurs dépôts de données (HAL, Nakala, Zenodo, ISTEX, arXiv, etc.) afin de simplifier et harmoniser la recherche d’informations.

- **Recherche unifiée**  
  - En centralisant les requêtes, l’utilisateur interagit uniquement avec un chatbot pour obtenir des résultats.  
  - Le chatbot prend en charge la synthèse et le formatage de l’information, assurant ainsi une présentation claire et accessible.

- **Fiabilité des sources**  
  - Les résultats proviennent directement des APIs officielles des dépôts, garantissant la crédibilité et la validité des données (titres, auteurs, dates, etc.).  
  - Les citations et informations bibliographiques bénéficient donc d’un niveau de fiabilité élevé.

- **Contrôle du recours aux LLM**  
  - Les modèles de langage (LLM) ne sont utilisés que pour la mise en forme et la coordination des résultats, et non comme source directe.  
  - Cette limitation réduit considérablement les risques de contenus inexacts (ou « hallucinations ») générés par les LLM.

### Fonctionnement

1. **Requête de l’utilisateur**  
   - L’utilisateur formule une requête via le chatbot.  
   - Le chatbot, grâce à sa capacité de synthèse, reformule ou clarifie si nécessaire, puis transmet la requête au serveur de l’application.

2. **Collecte et agrégation des données**  
   - Le serveur exécute la fonction de recherche (définie dans `main.py`), qui s’appuie sur différents scripts « subAPI » (`subapi_hal.py`, `subapi_nakala.py`, `subapi_zenodo.py`, `subapi_isidore.py`, `subapi_arxiv.py`, `subapi_istex.py`).  
   - Chacune de ces APIs spécialisées interroge un dépôt de données en temps réel.  
   - Les résultats sont agrégés via un `ThreadPoolExecutor`, puis structurés et retournés dans un format standardisé.

3. **Mise en forme et synthèse**  
   - Les données agrégées sont transmises au chatbot, qui les réorganise, met en forme les citations et peut fournir une synthèse condensée ou adaptée selon la demande de l’utilisateur.  
   - Ainsi, le chatbot joue un rôle de coordonateur, en plus de répondre directement aux questions.

4. **Renvoi des résultats**  
   - Une fois le processus terminé, le chatbot présente les résultats finaux à l’utilisateur.  
   - L’utilisateur obtient des références fiables (titres, DOIs, dates, etc.) et peut demander des résumés ou des extraits formatés selon ses besoins (markdown, texte brut, etc.).

5. **Extraction et traitement des documents (optionnel)**  
   - Dans certains cas, l’application peut récupérer et analyser les contenus de documents PDF (articles, rapports, etc.) via `fetcher.py` et `chunker.py`.  
   - Le script `fetcher.py` télécharge le PDF depuis le dépôt (HAL, Zenodo, Nakala, etc.), tandis que `chunker.py` découpe le texte en segments (chunks) pour un traitement plus fin (p. ex. éviter de dépasser certaines limites de taille).

---

En résumé, ce projet fournit un système modulaire et centralisé, reposant sur des APIs fiables, permettant d’interroger plusieurs dépôts de données. Le chatbot se charge alors d’en synthétiser et reformater les résultats, assurant une qualité et une cohérence optimales, tout en limitant le recours aux LLM pour réduire les risques de désinformation.

## Comment le redéployer

> **Note** : Ce projet est expérimental, développé initialement pour une instance de ChatGPT (ou tout autre moteur compatible) dans le but d’être utilisé au sein d’un “gpt” préconfiguré. Les instructions ci-dessous décrivent les grandes étapes pour le déployer et l’intégrer dans un chatbot.

### 1. Récupérer le dépôt

```bash
git clone https://github.com/SeidSmatti/LaCAS-GPT
cd LaCAS-GPT
```
### 2. Déployer les deux applications

Dans le dossier `LaCAS-GPT/src/`, vous trouverez deux répertoires principaux :

- `extractor/`
- `metadata/`

Chacun contient une application Flask (avec son propre `main.py` et son `requirements.txt`). Déployez-les indépendamment en utilisant la méthode de votre choix (ex. : Docker, Google Cloud Run, AWS, etc.).

#### Exemple : Sur Google Cloud Run, vous pouvez créer deux services distincts :

##### Service “extractor”
1. Placez-vous dans le dossier `extractor/` et construisez une image Docker.
2. Poussez l’image sur Google Container Registry ou un autre registre de conteneurs.
3. Créez un service Cloud Run en pointant sur cette image.

##### Service “metadata”
1. Répétez le même processus dans le dossier `metadata/`.

À l’issue de ces déploiements, vous disposerez de deux URLs (une pour l’API d’extraction et une pour l’API de métadonnées).

### 3. Créer un nouveau GPT

Dans votre interface de création de chatbot (ou de “gpt” préconfiguré) :
1. Créez deux “actions” (ou équivalents, selon la plateforme) correspondant chacune à l’une de vos APIs.
2. Utilisez le schéma OpenAPI approprié que vous trouverez dans le dossier `/schemas/` pour définir la structure des requêtes/réponses à vos services Flask. (Assurez-vous de renseigner l'URL de votre endpoint dans le champ approprié au début de chaque schéma)

### 4. Configurer le prompt

Dans la configuration de votre GPT/chatbot :
- Fournissez un prompt (instructions de conversation) adapté à l’utilisation de ces deux actions.
- Vous pouvez réutiliser ou adapter le prompt disponible dans le dossier `/prompts/`, qui est déjà optimisé pour nos APIs (format d’appel, champs obligatoires, etc.).

### 5. Interroger le chatbot

Une fois la configuration terminée, vous pouvez :
1. Poser une requête directement à votre nouveau GPT/chatbot.
2. Ce dernier fera appel aux APIs Flask (`extractor` et `metadata`) conformément aux schémas que vous avez déclarés.
3. Vous obtiendrez des résultats qui se veulent fiables (car issus des dépôts officiels) et pourrez bénéficier des capacités de reformattage et de synthèse offertes par votre GPT/chatbot.

---

## À propos
LaCAS GPT s'inscrit dans l'ambition du projet LaCAS dans son orientation vers plus d'automatisation des procédés à l'aide de l'intelligence artificielle. Il se veut comme un prototype de ce qui pourrait être développé dans le cadre du futur projet [LaCAS-IA](https://lacas.hypotheses.org/4287)

## Licence

Ce projet est sous licence GNU General Public License v3.0. Vous êtes libre d'utiliser, de modifier et de distribuer ce logiciel sous les conditions suivantes :

1. **Liberté d'utilisation** : Vous pouvez utiliser ce logiciel pour tout usage.
2. **Liberté d'étudier** : Vous pouvez étudier le fonctionnement du programme et le modifier selon vos besoins.
3. **Liberté de partage** : Vous pouvez redistribuer des copies du logiciel original.
4. **Liberté d'amélioration** : Vous pouvez distribuer des copies de vos versions modifiées, à condition de partager également le code source sous la même licence.

Pour plus de détails, veuillez vous référer au fichier `LICENCE` situé dans le même répertoire ou consulter le texte complet de la licence à l'adresse suivante : [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html).



