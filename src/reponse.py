"""Réponses documentaires en français, avec références contrôlées."""

import argparse
import json
import re
from decimal import Decimal

from src.recherche import PASSAGES, Recherche, charger, termes


HORS_PERIMETRE = re.compile(
    r"\b(?:licenciement|maternite|paternite|maladie professionnelle|heures supplementaires|"
    r"non renouvellement|fonction publique)\b"
)
CATEGORIE = re.compile(r"\b(?:cadres?|assimiles?|employes?|ouvriers?)\b")
DUREE = re.compile(r"\b(?:\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix) "
                   r"(?:an|ans|annees?|mois|semaines?|jours?)\b")

DUREES_ESSAI_CDI = (
    ({"cadre", "cadres", "assimile", "assimiles"}, "trois mois"),
    ({"employe", "employes", "employee", "employees"}, "un mois et demi"),
    ({"ouvrier", "ouvriers", "ouvriere", "ouvrieres"}, "quinze jours"),
)


NOMBRES = {
    mot: valeur for valeur, mot in enumerate(
        ("zero", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix")
    )
}
ANCIENNETE = re.compile(
    r"\b(\d+(?:[.,]\d+)?|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+"
    r"(mois|ans?|années?)\b"
)
REFERENCES_ENCADREES = frozenset({
    "code:13", "code:14", "code:34", "code:43", "code:44", "code:51",
    "code:231", "code:232", "code:238", "code:240", "decret:1",
})


def anciennete_en_mois(question):
    question = question.casefold()
    durees = list(ANCIENNETE.finditer(question))
    if len(durees) != 1 or re.search(
        r"\b(?:âgé|âgée|âge|et demi(?:e)?|presque|environ|moins de|plus de)\b", question.casefold()
    ):
        return None
    duree = durees[0]
    avant, apres = question[:duree.start()], question[duree.end():]
    if not (
        re.search(r"(?:depuis|après|au bout de)\s*$", avant)
        or re.match(r"\s+(?:d['’]ancienneté|de (?:travail|service))\b", apres)
    ):
        return None
    valeur, unite = duree.groups()
    nombre = Decimal(NOMBRES[valeur]) if valeur in NOMBRES else Decimal(valeur.replace(",", "."))
    return nombre if unite == "mois" else nombre * 12


def categorie_preavis(question):
    mots = set(termes(question))
    groupes = [categorie for categorie, _ in DUREES_ESSAI_CDI if categorie & mots]
    if len(groupes) != 1 or re.search(r"\b(?:pas|non)[ -]+(?:un |une )?(?:cadre|assimil|employ|ouvri)", question.casefold()):
        return None
    return "Cadres et assimilés" if groupes[0] == DUREES_ESSAI_CDI[0][0] else "Employés et ouvriers"


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
    "code:232": "L’article 232 prévoit 1,5 jour de travail effectif supplémentaire par "
                "période entière de cinq ans de service. La durée totale est plafonnée à "
                "30 jours de travail effectif.",
    "code:235": "Les interruptions de travail dues à la maladie ne sont pas décomptées "
                "du congé annuel payé selon cet article.",
    "code:236": "L’article exclut notamment les jours de repos hebdomadaire du décompte "
                "des jours de travail effectif.",
    "code:238": "Le Code fixe une équivalence en jours ou en heures. L’équivalence "
                "en heures diffère selon le caractère agricole de l’activité.",
    "code:240": "L’article 240 permet le fractionnement ou le cumul sur deux années "
                "consécutives par accord. Le fractionnement doit préserver une période "
                "d’au moins 12 jours ouvrables, dont deux jours de repos hebdomadaire.",
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
        if {"cdi", "cdd"} <= mots:
            return ("code:14",), "Ton contrat est-il un CDI ou un CDD ?"
        if not mots & {"cdd", "cdi", "courte", "courtes"}:
            return ("code:14",), "Es-tu en CDI ou en CDD ? Précise ta catégorie en CDI ou la durée du CDD."
        return ("code:14",), None
    if mots & {"conge", "conges", "vacances"}:
        if "preavis" in mots:
            return ("code:243",), None
        if mots & {"malade", "maladie", "ferie", "feries"}:
            return ("code:235",), None
        if "repos" in mots:
            return ("code:236",), None
        if mots & {"fractionner", "fractionnement", "cumuler", "cumul"} or "plusieurs fois" in q:
            return ("code:240",), None
        if "heures" in mots:
            if not mots & {"agricole", "agricoles"}:
                return ("code:238",), "Ton activité est-elle agricole ou non agricole ?"
            return ("code:238",), None
        if "majoration" in mots:
            return ("code:232",), None
        age = age_conges(question)
        if age is not None:
            return ("code:231",), None
        if anciennete_en_mois(question) is not None:
            return ("code:231",), "Quel âge as-tu ? La durée de service chez cet employeur a-t-elle été continue ?"
        return ("code:231",), "Quel âge as-tu et depuis combien de temps travailles-tu sans interruption chez cet employeur ?"
    depart_cdi = "cdi" in mots and bool(mots & {"quitte", "quitter", "partir", "pars"})
    if depart_cdi or mots & {"preavis", "demission", "demissionne", "demissionner", "quitter", "bareme"}:
        if mots & {"signature", "legaliser", "formalite"}:
            return ("code:34",), None
        if mots & {"notification", "notifie", "notifiee"} and mots & {"partir", "court", "commence", "demarre"}:
            return ("code:44",), None
        if "indemnite" in mots and "preavis" in mots:
            return ("code:51",), None
        if "cdi" not in mots or "cdd" in mots:
            if "cdd" in mots and "cdi" not in mots:
                return (), None
            return ("code:34", "code:43"), "Quel est ton type de contrat et es-tu encore en période d’essai ?"
        references = ("code:43", "decret:1")
        categorie = categorie_preavis(question)
        anciennete = anciennete_en_mois(question)
        if categorie is None and anciennete is None:
            return references, "Quelle est ta catégorie professionnelle et quelle est ton ancienneté ?"
        if categorie is None:
            return references, "Quelle est ta catégorie professionnelle : cadre ou assimilé, employé, ou ouvrier ?"
        if anciennete is None:
            return references, "Quelle est ton ancienneté chez cet employeur, en mois ou en années ?"
        return references, None
    return (), None


def age_conges(question):
    mots = set(termes(question))
    majeur = bool(mots & {"majeur", "majeure", "adulte"})
    mineur = bool(mots & {"mineur", "mineure"})
    ages = re.findall(
        r"\b(?:j['’]ai|âgé(?:e)? de|(?:salarié|salariée) de)\s+(\d{1,3})\s+ans\b",
        question.casefold(),
    )
    if majeur and not mineur:
        return "majeur"
    if mineur and not majeur:
        return "mineur"
    if len(set(ages)) == 1 and not (majeur or mineur):
        return "mineur" if int(ages[0]) < 18 else "majeur"
    return None


def expliquer_conges(question):
    age = age_conges(question)
    if age is None:
        return EXPLICATIONS["code:231"]
    taux = "2 jours" if age == "mineur" else "1,5 jour"
    return (
        f"L’article 231 prévoit {taux} de travail effectif par mois de service pour "
        "cette tranche d’âge. Le droit au congé annuel s’ouvre après six mois de service "
        "continu chez le même employeur ou dans la même entreprise, sous réserve de "
        "dispositions plus favorables."
    )


def expliquer_essai_cdd(question):
    duree = re.search(r"\bcdd de (\d+|un|deux|trois|quatre|cinq|six|sept|huit|neuf|dix) mois\b", question.casefold())
    if not duree:
        return EXPLICATIONS["code:14"]
    valeur = duree[1]
    mois = NOMBRES[valeur] if valeur in NOMBRES else int(valeur)
    if mois <= 0:
        return EXPLICATIONS["code:14"]
    if mois < 6:
        regle = "un jour par semaine de travail, dans la limite de deux semaines"
    elif mois > 6:
        regle = "un mois"
    else:
        return (
            "L’article 14 distingue les CDD de moins de six mois et ceux de plus de six mois. "
            "Le passage ne fixe pas explicitement le plafond pour un CDD de six mois exactement."
        )
    return f"Selon l’article 14, le plafond correspond à {regle}. Une durée plus courte peut être prévue."


def expliquer(reference, question):
    if reference == "code:231":
        return expliquer_conges(question)
    if reference == "code:14":
        mots = set(termes(question))
        if "cdd" in mots and "cdi" not in mots:
            return expliquer_essai_cdd(question)
        if "cdi" in mots and "cdd" not in mots:
            durees = [duree for categorie, duree in DUREES_ESSAI_CDI if categorie & mots]
            if len(durees) == 1:
                return (
                    f"Selon l’article 14, la durée initiale de la période d’essai en CDI "
                    f"est de {durees[0]} pour cette catégorie. "
                    "Elle peut être renouvelée une fois. Le contrat de travail, la convention "
                    "collective ou le règlement intérieur peuvent prévoir une durée plus courte."
                )
    return EXPLICATIONS[reference]


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
            "message": "\n\n".join(expliquer(ref, question) for ref in references),
            "sources": sources,
        }
        if "decret:1" in references:
            bareme = self.passages["decret:1"]["bareme"]
            categorie = categorie_preavis(question)
            anciennete = anciennete_en_mois(question)
            ligne = next((ligne for ligne in bareme if ligne["categorie"] == categorie), None)
            if ligne is None or anciennete is None:
                return {
                    "statut": "source_insuffisante",
                    "message": "Je ne peux pas déterminer une durée à partir du barème chargé.",
                    "sources": [],
                }
            if anciennete < 12:
                tranche = "moins_un_an"
            elif anciennete <= 60:
                tranche = "un_a_cinq_ans"
            else:
                tranche = "plus_de_cinq_ans"
            resultat["message"] = (
                f"Le délai de préavis de référence est de {ligne[tranche]} selon le décret n° 2-04-469. "
                "Vérifie les exceptions et les dispositions applicables, notamment celles de ton "
                "contrat ou de ta convention collective, comme le prévoit l’article 43."
            )
            resultat["bareme"] = bareme
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
