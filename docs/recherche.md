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
