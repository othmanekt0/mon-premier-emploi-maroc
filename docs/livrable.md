# Livrable Python 1.0.0

Depuis la racine du dépôt, avec Python 3.11 ou 3.12 :

```powershell
python -m pip install build
python -m build
```

La commande produit la roue `mon_premier_emploi_maroc-1.0.0-py3-none-any.whl` et l’archive source `mon_premier_emploi_maroc-1.0.0.tar.gz` dans `dist/`. La roue inclut le code, le catalogue des sources et le barème structuré. Le PDF officiel et les passages générés sont préparés à part.

## Installation hors du dépôt

Dans un dossier de travail neuf, avec la roue et le [PDF officiel du Code du travail](https://adala.justice.gov.ma/api/uploads/2024/04/30/code%20du%20travail-1714463246806.pdf) copiés dans ce dossier sous les noms indiqués :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .\mon_premier_emploi_maroc-1.0.0-py3-none-any.whl
.\.venv\Scripts\emploi-preparer.exe --code .\code-du-travail.pdf --sortie .\passages.json
$env:EMPLOI_PASSAGES = (Resolve-Path .\passages.json).Path
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

Laisser l’API ouverte. [La route de santé](http://127.0.0.1:8001/health) doit indiquer 15 passages. Dans un deuxième PowerShell, depuis le même dossier :

```powershell
$env:API_URL = "http://127.0.0.1:8001"
.\.venv\Scripts\emploi-ui.exe
```

Ouvrir [Streamlit](http://localhost:8501). Par exemple, une question sur la durée d’essai pour un cadre en CDI doit afficher la durée et la citation de l’article 14. Une question de préavis sans ancienneté ni catégorie doit demander ces précisions.

Le mode par règles est activé par défaut. Le [mode génératif local](reponse.md#mode-génératif-local) demande Ollama et reste expérimental. Le [guide du corpus](corpus.md) et le [rapport d’évaluation](evaluation.md) détaillent les sources, les résultats et les limites observées.
