# Mon premier emploi au Maroc

Assistant de recherche documentaire pour les salariés du secteur privé au Maroc. Le projet couvre la période d’essai, les congés annuels payés et le préavis de démission. L’agent expliquera les règles en français et citera les passages officiels sur lesquels il s’appuie.

## État du projet

Le cadrage est disponible dans la [fiche projet](docs/cadrage.md). Le corpus, la recherche, l’API et l’interface sont disponibles en local.

## Organisation

| Dossier | Rôle |
| --- | --- |
| `data/` | Références des documents officiels et données de démonstration. |
| `src/` | Préparation du corpus et construction de l’index. |
| `api/` | API FastAPI. |
| `ui/` | Interface Streamlit. |
| `tests/` | Évaluation de la recherche et des réponses, puis tests d’intégration. |
| `docs/` | Cadrage et journal du projet. |

## Tester le projet sous Windows

Ouvrir PowerShell à la racine du projet. Utiliser Python 3.11 ou 3.12 pour créer l’environnement du projet.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

L’API a besoin de `data/index/passages.json`. Si ce fichier manque, télécharger le [PDF officiel du Code du travail](https://adala.justice.gov.ma/api/uploads/2024/04/30/code%20du%20travail-1714463246806.pdf) et indiquer son chemin réel à la commande suivante :

```powershell
.\.venv\Scripts\python.exe src/preparer_passages.py --code "C:\chemin\vers\code-du-travail.pdf"
```

### Terminal 1 — Lancer et essayer l’API

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Laisser ce terminal ouvert. Attendre le message `Application startup complete`, puis ouvrir [la vérification de santé](http://127.0.0.1:8000/health). Elle doit afficher `{"status":"OK","passages":15}`. Ces adresses sont locales à ta machine et deviennent accessibles lorsque l’API tourne.

Dans [la documentation interactive](http://127.0.0.1:8000/docs), ouvrir `POST /question`, cliquer sur **Try it out**, coller le JSON ci-dessous, puis cliquer sur **Execute**.

```json
{"question": "Quelle est la durée d’essai prévue pour un cadre en CDI ?"}
```

Résultat attendu : HTTP 200, statut `repondre` et source `code:14`. Avec `{"question": ""}`, le résultat attendu est HTTP 422.

### Terminal 2 — Lancer et essayer l’interface

Ouvrir un deuxième PowerShell à la racine du projet, en laissant l’API tourner.

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```

Ouvrir [l’interface locale](http://localhost:8501), puis essayer ces questions.

| Question | Résultat attendu |
| --- | --- |
| Quelle est la durée d’essai prévue pour un cadre en CDI ? | Réponse avec l’article 14 et un lien vers la source officielle. |
| Je démissionne de mon CDI. Combien de temps dure mon préavis ? | L’interface demande la catégorie professionnelle et l’ancienneté. |
| Quel barème de préavis s’applique à un cadre en CDI avec deux ans d’ancienneté ? | Réponse avec le barème, l’article 43 et le décret. |
| Combien de jours de congé de maternité puis-je prendre ? | Question hors périmètre. |

Si le port 8000 est déjà occupé, démarrer Uvicorn avec `--port 8001`, ouvrir `http://127.0.0.1:8001/docs` et exécuter `$env:API_URL = "http://127.0.0.1:8001"` dans le deuxième terminal avant de lancer Streamlit.

## Mode génératif local

Le [guide Ollama](docs/reponse.md#mode-génératif-local) explique comment activer et évaluer la génération avec citations vérifiées.

## Tests automatisés

Après avoir préparé le corpus :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Vérification sur GitHub

À chaque push et pull request, le [workflow Tests](../../actions/workflows/tests.yml) utilise Python 3.11, télécharge le PDF officiel référencé dans le catalogue, génère les passages et exécute les tests. Le bilan de recherche est visible dans le journal du workflow.

## Livrable installable

Le [guide du livrable](docs/livrable.md) explique comment construire la roue et l’archive source, puis installer et lancer l’application hors du dépôt.
