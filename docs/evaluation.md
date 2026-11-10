# Évaluation initiale sur des formulations nouvelles

Le [jeu d’évaluation](../tests/cas_evaluation.json) contient quinze questions, cinq par thème. Il est distinct des trente cas de régression. Chaque question indique le comportement, les références et le contenu attendu. Quelques formulations reprennent des exemples exploratoires déjà essayés, mais aucune n’a servi à modifier la version évaluée.

## Reproduire la mesure

Après avoir [préparé les passages](corpus.md), lancer depuis la racine du dépôt :

```powershell
python -m src.evaluer_reponses
```

Le script compare les statuts, vérifie si les références attendues figurent parmi les cinq premiers résultats BM25 et vérifie leur présence dans les sources de la réponse. Il affiche la réponse et le critère de lecture pour permettre un contrôle humain. Une référence présente peut être pertinente sans que l’explication soit suffisante.

## Résultats de référence

Moteur évalué à partir du commit `ff2b026`.

| Mesure | Résultat |
| --- | --- |
| Statut correct | 8/15 |
| Réponse produite lorsque demandée | 4/9 |
| Clarification demandée lorsque nécessaire | 1/3 |
| Abstention sur les questions hors périmètre | 3/3 |
| Toutes les références attendues dans les cinq premiers résultats BM25 | 9/12 |
| Toutes les références attendues présentes dans les sources de la réponse | 5/12 |

Les trois questions hors périmètre n’ont pas de référence attendue et sont exclues des deux dernières mesures. Le contenu des réponses est à vérifier avec les critères de lecture. Les chiffres ci-dessus mesurent le comportement et la présence des sources.

Le moteur classe à tort plusieurs demandes dans « hors périmètre », notamment une question sur la période probatoire et des questions formulées avec « vacances » ou « quitter mon CDI ». Il demande aussi des précisions inutiles pour le fractionnement des congés et le point de départ du préavis.

Ce jeu sert à comparer les versions. S’il est utilisé pour orienter les corrections, prévoir ensuite un autre jeu de questions inédites pour mesurer la généralisation.
