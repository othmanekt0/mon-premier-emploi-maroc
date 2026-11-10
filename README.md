# Mon premier emploi au Maroc

Assistant de recherche documentaire pour les salariés du secteur privé au Maroc. Le projet couvre la période d’essai, les congés annuels payés et le préavis de démission. L’agent expliquera les règles en français et citera les passages officiels sur lesquels il s’appuie.

## État du projet

Le cadrage est disponible dans la [fiche projet](docs/cadrage.md). Le corpus, le moteur de recherche et l’application seront ajoutés au fil des étapes.

## Organisation

| Dossier | Rôle |
| --- | --- |
| `data/` | Références des documents officiels et données de démonstration. |
| `src/` | Préparation du corpus et construction de l’index. |
| `api/` | API FastAPI. |
| `ui/` | Interface Streamlit. |
| `tests/` | Évaluation de la recherche et des réponses, puis tests d’intégration. |
| `docs/` | Cadrage et journal du projet. |

## API locale

Préparer le corpus selon le [guide du corpus](docs/corpus.md), puis lancer :

```powershell
python -m uvicorn api.main:app --reload
```

La documentation interactive est disponible sur http://127.0.0.1:8000/docs.
La route `GET /health` vérifie le chargement du corpus. La route `POST /question`
accepte un objet JSON comme `{"question": "Je démissionne de mon CDI. Quel est mon préavis ?"}`.
Elle renvoie le statut, le message et les sources. Les questions vides ou de plus
de 2 000 caractères sont rejetées avec un statut HTTP 422.

Pour lancer les tests après préparation du corpus :

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```
