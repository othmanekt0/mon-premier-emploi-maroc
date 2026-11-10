# Réponses sourcées

Après avoir [préparé les passages](corpus.md), lancer depuis la racine du dépôt :

```powershell
python -m src.reponse "Je démissionne de mon CDI. Combien de temps dure mon préavis ?"
python -m unittest discover -s tests -p "test_reponse.py" -v
```

La première version combine des règles d’orientation et des explications rédigées à l’avance. Le moteur lexical classe les références retenues pour la question. Les règles peuvent également sélectionner une référence nécessaire même si elle est mal classée. Chaque citation provient des passages préparés et le barème du décret reste présenté comme une donnée structurée.

La sortie JSON distingue quatre situations :

- `repondre` fournit une explication et les sources.
- `clarifier` demande une information et peut montrer les sources pertinentes. Pour l’instant, soumettre de nouveau une question complète avec la précision.
- `hors_perimetre` indique les sujets couverts.
- `source_insuffisante` signale une référence nécessaire absente du corpus chargé.

Les tests vérifient les statuts et les références sur les 30 cas du projet, ainsi que la provenance des citations, l’absence d’une source et le traitement du barème. Ces cas servent de tests de régression. Ils ne mesurent pas la couverture de questions nouvelles ni la justesse juridique de réponses personnalisées.


## Mode génératif local

Le mode par règles reste le mode par défaut. Pour essayer Qwen3 via [Ollama](https://docs.ollama.com/capabilities/structured-outputs), préparer le corpus et vérifier qu’Ollama tourne. Depuis PowerShell :

```powershell
ollama list
$env:OLLAMA_MODEL = "qwen3:1.7b"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

Le modèle choisi doit apparaître dans `ollama list`. Au besoin, le télécharger avec `ollama pull qwen3:1.7b`. Pour utiliser Streamlit avec ce serveur, définir `$env:API_URL = "http://127.0.0.1:8001"` dans le terminal qui lance l’interface.

L’API envoie au modèle local les cinq passages classés par BM25. Elle valide le format JSON et exige que chaque extrait cité existe dans le passage indiqué. Les identifiants et les liens affichés proviennent du corpus. Ce contrôle garantit la provenance de l’extrait. La pertinence de l’explication et l’applicabilité du texte restent à vérifier séparément. Le mode génératif s’abstient si une réponse présente une citation invérifiable ou si Ollama est inaccessible.

Pour comparer les réponses, lancer `python -m src.evaluer_reponses --ollama qwen3:1.7b`. Les tests automatisés simulent le modèle pour reproduire les contrôles sans télécharger ses poids en CI.
