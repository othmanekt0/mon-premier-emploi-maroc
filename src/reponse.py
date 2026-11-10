"""Réponses documentaires en français, avec références contrôlées."""

import argparse
import json
import re

from src.recherche import PASSAGES, Recherche, charger, termes


HORS_PERIMETRE = re.compile(
    r"\b(?:licenciement|maternite|maladie professionnelle|heures supplementaires|"
    r"non renouvellement|fonction publique)\b"
)
CATEGORIE = re.compile(r"\b(?:cadres?|assimiles?|employes?|ouvriers?)\b")
DUREE = re.compile(r"\b(?:\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix) "
                   r"(?:an|ans|annees?|mois|semaines?|jours?)\b")

EXPLICATIONS = {
    "code:13": "Le Code distingue le principe de rupture pendant l’essai et les cas "
               "où un délai s’applique. La durée travaillée, la fréquence de paie et le motif comptent.",
    "code:14": "En CDI, la durée de l’essai dépend de la catégorie professionnelle et "
               "l’article prévoit un seul renouvellement. En CDD, le plafond dépend de la durée du contrat. "
               "Vérifie aussi si ton contrat prévoit une durée plus courte.",
    "code:34": "Le Code prévoit une démission avec signature légalisée pour mettre fin "
               "à un CDI à l’initiative du salarié.",
    "code:43": "Pour un CDI, vérifie la règle de préavis, ses exceptions et les dispositions "
               "applicables dans ton contrat ou ta convention collective.",
    "code:44": "Selon cet article, le préavis commence le lendemain de la notification.",
    "code:51": "Cet article décrit l’indemnité qui peut être due à l’autre partie lorsqu’un "
               "préavis de CDI n’est pas respecté intégralement, sous les conditions qu’il précise.",
    "code:231": "Le calcul de base dépend de l’âge et des mois de service. L’article "
                "prévoit six mois de service continu pour le droit au congé et réserve les règles plus favorables.",
    "code:232": "L’article prévoit une majoration par période entière de cinq ans de "
                "service, dans la limite de la durée totale qu’il fixe.",
    "code:235": "Les interruptions de travail dues à la maladie ne sont pas décomptées "
                "du congé annuel payé selon cet article.",
    "code:236": "L’article exclut notamment les jours de repos hebdomadaire du décompte "
                "des jours de travail effectif.",
    "code:238": "Le Code fixe une équivalence en jours ou en heures. L’équivalence "
                "en heures diffère selon le caractère agricole de l’activité.",
    "code:240": "Le fractionnement ou le cumul est possible par accord, dans les limites "
                "indiquées par l’article.",
    "code:243": "Le Code distingue la durée du congé annuel payé du délai de préavis.",
    "decret:1": "Repère la ligne du barème correspondant à la catégorie professionnelle et à l’ancienneté.",
}


def orienter(question):
    q = " ".join(termes(question))
    mots = set(q.split())
    if HORS_PERIMETRE.search(q):
        return (), None
    if "essai" in mots:
        if mots & {"rupture", "fin", "rompre", "prevenu", "prevenir"}:
            if not DUREE.search(q) or not mots & {"paye", "payee", "paie", "remunere"}:
                return ("code:13",), "Depuis combien de temps travailles-tu et à quelle fréquence es-tu payé ?"
            return ("code:13",), None
        if not mots & {"cdd", "cdi", "courte", "courtes"}:
            return ("code:14",), "Es-tu en CDI ou en CDD ? Précise ta catégorie en CDI ou la durée du CDD."
        return ("code:14",), None
    if mots & {"conge", "conges"}:
        if "preavis" in mots:
            return ("code:243",), None
        if mots & {"malade", "maladie", "ferie", "feries"}:
            return ("code:235",), None
        if "repos" in mots:
            return ("code:236",), None
        if mots & {"fractionner", "fractionnement", "cumuler", "cumul"}:
            return ("code:240",), None
        if "heures" in mots:
            if not mots & {"agricole", "agricoles"}:
                return ("code:238",), "Ton activité est-elle agricole ou non agricole ?"
            return ("code:238",), None
        if "majoration" in mots:
            return ("code:232",), None
        if mots & {"age", "ans", "majeur", "mineur"} or DUREE.search(q):
            return ("code:231",), None
        return ("code:231",), "Quel âge as-tu et depuis combien de temps travailles-tu sans interruption chez cet employeur ?"
    if mots & {"preavis", "demission", "demissionne", "demissionner", "quitter", "bareme"}:
        if mots & {"signature", "legaliser", "formalite"}:
            return ("code:34",), None
        if "notification" in mots and mots & {"partir", "court", "commence"}:
            return ("code:44",), None
        if "indemnite" in mots and "preavis" in mots:
            return ("code:51",), None
        if "cdi" not in mots:
            if "cdd" in mots:
                return (), None
            return ("code:34", "code:43"), "Quel est ton type de contrat et es-tu encore en période d’essai ?"
        if not CATEGORIE.search(q) or not DUREE.search(q):
            return ("code:43", "decret:1"), "Quelle est ta catégorie professionnelle et quelle est ton ancienneté ?"
        return ("code:43", "decret:1"), None
    return (), None


class Assistant:
    def __init__(self, passages):
        self.passages = {p["id"]: p for p in passages}
        self.recherche = Recherche(passages)

    def repondre(self, question):
        references, precision = orienter(question)
        if not references:
            return {
                "statut": "hors_perimetre",
                "message": "Je couvre la période d’essai, les congés annuels payés et le préavis de démission en CDI.",
                "sources": [],
            }
        if any(ref not in self.passages for ref in references):
            return {
                "statut": "source_insuffisante",
                "message": "Le corpus chargé ne contient pas toutes les références nécessaires.",
                "sources": [],
            }

        candidats = [p["id"] for p, _ in self.recherche.chercher(question, len(self.passages))]
        ordre = [ref for ref in candidats if ref in references]
        ordre.extend(ref for ref in references if ref not in ordre)
        sources = [
            {cle: self.passages[ref][cle] for cle in ("id", "article", "titre", "url", "nature", "texte", "page_pdf")}
            for ref in ordre
        ]
        if precision:
            return {"statut": "clarifier", "message": precision, "sources": sources}
        resultat = {
            "statut": "repondre",
            "message": "\n\n".join(EXPLICATIONS[ref] for ref in references),
            "sources": sources,
        }
        if "decret:1" in references:
            resultat["bareme"] = self.passages["decret:1"]["bareme"]
        return resultat


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question")
    args = parser.parse_args()
    if not PASSAGES.is_file():
        parser.error("Passages introuvables. Lancez d’abord src/preparer_passages.py.")
    print(json.dumps(Assistant(charger(PASSAGES)).repondre(args.question), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
