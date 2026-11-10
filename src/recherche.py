"""Recherche lexicale dans les passages juridiques préparés."""

import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASSAGES = ROOT / "data/index/passages.json"
CAS = ROOT / "tests/cas_reference.json"
MOTS_VIDES = set(
    "ai au aux avec ce ces dans de des du elle en est et il je l la le les "
    "leur lui ma mes mon ne notre nous on ou par pas pour puis que quel "
    "quelle quels quelles qui sa se ses son sur un une y a d s t".split()
)


def charger(chemin):
    return json.loads(chemin.read_text(encoding="utf-8"))


def termes(texte):
    normalise = unicodedata.normalize("NFKD", texte.casefold())
    sans_accents = "".join(c for c in normalise if not unicodedata.combining(c))
    return [mot for mot in re.findall(r"[a-z0-9]+", sans_accents) if mot not in MOTS_VIDES]


class Recherche:
    def __init__(self, passages):
        if not passages:
            raise ValueError("Le corpus de recherche est vide")
        self.passages = passages
        self.documents = []
        frequences = Counter()
        for passage in passages:
            contenu = " ".join(passage[champ] for champ in ("titre", "resume", "texte"))
            if "bareme" in passage:
                contenu += " " + " ".join(
                    valeur for ligne in passage["bareme"] for valeur in ligne.values()
                )
            document = Counter(termes(contenu))
            self.documents.append(document)
            frequences.update(document.keys())
        self.longueur_moyenne = sum(map(Counter.total, self.documents)) / len(passages)
        self.idf = {
            mot: math.log1p((len(passages) - nombre + 0.5) / (nombre + 0.5))
            for mot, nombre in frequences.items()
        }

    def chercher(self, question, limite=5):
        if limite < 1:
            raise ValueError("La limite doit être positive")
        requete = set(termes(question)) & self.idf.keys()
        resultats = []
        for passage, document in zip(self.passages, self.documents):
            normalisation = 1.2 * (0.25 + 0.75 * document.total() / self.longueur_moyenne)
            score = sum(
                self.idf[mot] * (2.2 * document[mot]) / (document[mot] + normalisation)
                for mot in sorted(requete)
                if mot in document
            )
            if score > 0:
                resultats.append((passage, score))
        return sorted(resultats, key=lambda r: (-r[1], r[0]["id"]))[:limite]


def evaluer(moteur, cas, limite):
    avec_references = [c for c in cas if c["references"]]
    premiers = 0
    complets = 0
    trouves = 0
    attendus = 0
    for exemple in avec_references:
        references = set(exemple["references"])
        resultats = [p["id"] for p, _ in moteur.chercher(exemple["question"], limite)]
        premiers += bool(set(resultats[:1]) & references)
        complets += references <= set(resultats)
        trouves += len(references & set(resultats))
        attendus += len(references)
        if references - set(resultats):
            print(f"{exemple['id']} : références manquantes {sorted(references - set(resultats))}")
    print(f"Cas avec une référence attendue en première position : {premiers}/{len(avec_references)}")
    print(f"Cas avec toutes leurs références dans les {limite} premiers : {complets}/{len(avec_references)}")
    print(f"Références retrouvées : {trouves}/{attendus}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--question")
    action.add_argument("--evaluer", action="store_true")
    parser.add_argument("--passages", type=Path, default=PASSAGES)
    parser.add_argument("--limite", type=int, default=5)
    args = parser.parse_args()
    if args.limite < 1:
        parser.error("--limite doit être positive")
    if not args.passages.is_file():
        parser.error("Passages introuvables. Lancez d’abord src/preparer_passages.py.")
    moteur = Recherche(charger(args.passages))
    if args.evaluer:
        evaluer(moteur, charger(CAS), args.limite)
    else:
        for passage, score in moteur.chercher(args.question, args.limite):
            print(f"{passage['id']} | {score:.2f} | {passage['titre']} | {passage['url']}")


if __name__ == "__main__":
    main()
