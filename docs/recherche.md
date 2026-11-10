# Évaluation du moteur de recherche

Après avoir généré les passages selon le [guide du corpus](corpus.md), lancer depuis la racine du dépôt :

```powershell
python src/recherche.py --question "Quel est mon préavis si je démissionne de mon CDI ?"
python src/recherche.py --evaluer
```

Le moteur utilise BM25 pour classer les passages à partir des mots de la question. Il consulte le titre, le résumé, le texte et, le cas échéant, les valeurs du barème. Les scores servent au classement et ne représentent pas une probabilité. Chaque résultat conserve l’identifiant de l’article et le lien officiel.

## Première mesure

| Indicateur | Résultat |
| --- | --- |
| Une référence attendue en première position | 22 sur 24 questions |
| Toutes les références attendues dans les cinq premiers résultats | 22 sur 24 questions |
| Références attendues retrouvées dans les cinq premiers résultats | 26 sur 28 références |

Les deux références manquées sont l’article 235 dans le cas de maladie pendant les congés et l’article 43 dans la question de préavis sans ancienneté ni catégorie. Cette mesure porte sur le jeu de référence du projet. Les six cas hors périmètre n’ont pas d’article cible et sont exclus de ces chiffres. La clarification, l’abstention et la fidélité des réponses devront être évaluées quand la génération sera disponible.


## Recherche sémantique et hybride

Installer la dépendance optionnelle, puis lancer la comparaison depuis la racine du dépôt après avoir préparé les passages.

```powershell
python -m pip install -r requirements-semantiques.txt
python -m src.recherche_hybride --comparer
python -m src.recherche_hybride --question "J’ai droit à combien de jours de vacances ?"
```

FastEmbed encode localement les titres et résumés des articles avec le [modèle multilingue MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2). La première exécution télécharge le modèle dans `data/index/modeles/`. Le classement sémantique utilise la similarité cosinus. La fusion RRF combine les rangs des deux listes, chacune avec cinq candidats lors de cette comparaison.

Sur les douze questions annotées du [jeu d’évaluation](evaluation.md) :

| Classement | Une référence attendue en première position | Toutes les références attendues dans les cinq premières |
| --- | --- | --- |
| BM25 | 10/12 | 9/12 |
| Sémantique | 6/12 | 6/12 |
| Hybride | 5/12 | 10/12 |

La fusion retrouve toutes les références sur une question supplémentaire, mais place moins souvent une référence attendue en tête. Le classement hybride est disponible dans la commande d’évaluation. L’API continue d’utiliser BM25 et les règles de réponse existantes. Les trois cas hors périmètre sont exclus de la comparaison, qui mesure la recherche documentaire.
