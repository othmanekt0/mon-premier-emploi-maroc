# Fiche de cadrage

## Besoin

Aider un jeune salarié à comprendre une règle du travail et à retrouver le texte officiel qui s’applique à sa question.

## Public

Salariés du secteur privé au Maroc, notamment les personnes qui signent ou quittent leur premier emploi.

## Périmètre

- Période d’essai.
- Congés annuels payés.
- Préavis en cas de démission.

La première version accepte des questions en français et en texte libre. L’import de contrats est prévu pour une version ultérieure.

## Approche et justification

Le système utilise une approche RAG. Il recherche les articles pertinents dans le corpus officiel et explique les passages retrouvés. Les références permettent à l’utilisateur de vérifier la réponse.

## Données nécessaires

Le [Code du travail publié sur Adala](https://adala.justice.gov.ma/api/uploads/2024/04/30/code%20du%20travail-1714463246806.pdf) sert de point de départ. Les textes d’application et les versions pertinentes seront vérifiés avant leur intégration. Chaque passage conservera son article, son URL et les informations de version disponibles.

## Réponse attendue

Une explication en français simple, le numéro de l’article, le passage utilisé et un lien officiel. Si un fait déterminant manque, l’assistant pose une question ciblée. Il indique lorsque la demande sort du périmètre ou que les sources sont insuffisantes.

## Évaluation

Préparer 30 cas, à raison de 10 par thème. Noter séparément la présence des articles attendus dans les résultats de recherche, la fidélité de l’explication aux sources et la gestion des cas incomplets ou hors périmètre.

## Risques

Une source obsolète ou une citation hors contexte peut conduire l’utilisateur à une mauvaise décision. L’assistant indique les éléments qui dépendent du contrat ou de la situation et évite de conclure lorsque les textes consultés sont insuffisants.
