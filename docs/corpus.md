# Corpus officiel

La première sélection couvre les questions de période d’essai, de congés annuels payés et de préavis de démission dans le secteur privé au Maroc.

| Thème | Références retenues |
| --- | --- |
| Période d’essai | Code du travail, articles 13 et 14 |
| Congés annuels payés | Code du travail, articles 231, 232, 235 à 238, 240 et 243 |
| Préavis de démission | Code du travail, articles 34, 43, 44 et 51. Décret n° 2-04-469, article premier |

- [Code du travail en français sur Adala](https://adala.justice.gov.ma/api/uploads/2024/04/30/code%20du%20travail-1714463246806.pdf)
- [Décret au Bulletin officiel n° 5280, page 23](https://www.sgg.gov.ma/BO/bo_fr/2005/BO_5280_Fr.pdf#page=23)
- [Catalogue des articles et de leurs sources](../data/corpus.json)

Le catalogue contient des résumés de repérage. Les articles originaux restent consultables aux liens officiels. L’étape d’indexation devra conserver la référence de chaque passage et distinguer le texte officiel du résumé. Les dates indiquées identifient les textes et leur publication. Avant la mise en service, vérifier les versions et les dispositions complémentaires nécessaires aux cas retenus.

## Préparer les passages et les cas de référence

Télécharger le PDF du Code du travail depuis le lien Adala ci-dessus. Depuis la racine du dépôt, exécuter :

```powershell
python -m pip install -r requirements.txt
python src/preparer_passages.py --code "<chemin vers le PDF Adala>"
```

Le fichier généré `data/index/passages.json` contient les articles du Code extraits et les références vers leurs pages. Le Bulletin officiel est scanné. Son barème est enregistré séparément sous forme structurée et identifié comme tel dans la sortie. Pour citer sa formulation exacte, consulter la page officielle.

Les [30 cas de référence](../tests/cas_reference.json) indiquent les références attendues et le comportement attendu. Chaque thème comprend six questions auxquelles répondre, deux qui nécessitent une clarification et deux hors périmètre. Les références utilisent le format `source:article`. Ce jeu servira à évaluer le moteur quand il sera disponible.
