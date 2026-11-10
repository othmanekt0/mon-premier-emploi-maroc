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
