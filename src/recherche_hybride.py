"""Recherche sémantique locale et fusion avec BM25."""

import argparse
import math

from src.evaluer_reponses import CAS
from src.recherche import PASSAGES, Recherche, charger

MODELE = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CACHE = PASSAGES.parent / "modeles"


class RechercheSemantique:
    def __init__(self, passages):
        from fastembed import TextEmbedding

        self.passages = passages
        self.encodeur = TextEmbedding(model_name=MODELE, cache_dir=str(CACHE), threads=2)
        # Les résumés courts représentent chaque article sans tronquer son objet.
        textes = [f"{p['titre']}. {p['resume']}" for p in passages]
        self.vecteurs = list(self.encodeur.embed(textes))

    def chercher(self, question, limite=5):
        if limite < 1:
            raise ValueError("La limite doit être positive")
        if not question.strip():
            return []
        requete = next(self.encodeur.embed([question]))
        norme_requete = math.sqrt(float(requete @ requete))
        resultats = []
        for passage, vecteur in zip(self.passages, self.vecteurs, strict=True):
            norme = norme_requete * math.sqrt(float(vecteur @ vecteur))
            if norme:
                resultats.append((passage, float(requete @ vecteur) / norme))
        return sorted(resultats, key=lambda r: (-r[1], r[0]["id"]))[:limite]


class RechercheHybride:
    def __init__(self, lexicale, semantique):
        self.lexicale = lexicale
        self.semantique = semantique

    def chercher(self, question, limite=5):
        if limite < 1:
            raise ValueError("La limite doit être positive")
        profondeur = max(5, limite)
        classements = (
            self.lexicale.chercher(question, profondeur),
            self.semantique.chercher(question, profondeur),
        )
        scores = {}
        passages = {}
        for classement in classements:
            for rang, (passage, _) in enumerate(classement, start=1):
                identifiant = passage["id"]
                passages[identifiant] = passage
                scores[identifiant] = scores.get(identifiant, 0) + 1 / (60 + rang)
        return sorted(
            ((passages[identifiant], score) for identifiant, score in scores.items()),
            key=lambda r: (-r[1], r[0]["id"]),
        )[:limite]


def comparer(moteurs, cas):
    compteurs = {nom: [0, 0] for nom in moteurs}
    avec_references = [exemple for exemple in cas if exemple["references"]]
    for exemple in avec_references:
        attendues = set(exemple["references"])
        for nom, moteur in moteurs.items():
            ids = [p["id"] for p, _ in moteur.chercher(exemple["question"])]
            compteurs[nom][0] += bool(attendues.intersection(ids[:1]))
            compteurs[nom][1] += attendues.issubset(ids)
            if not attendues.issubset(ids):
                print(f"{nom} | {exemple['id']} | références manquantes : {sorted(attendues - set(ids))}")
    for nom, (premiers, complets) in compteurs.items():
        total = len(avec_references)
        print(f"{nom} | première position : {premiers}/{total} | toutes dans le top 5 : {complets}/{total}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--question")
    action.add_argument("--comparer", action="store_true")
    args = parser.parse_args()
    if not PASSAGES.is_file():
        parser.error("Passages introuvables. Lancez d’abord src/preparer_passages.py.")
    passages = charger(PASSAGES)
    lexicale = Recherche(passages)
    semantique = RechercheSemantique(passages)
    hybride = RechercheHybride(lexicale, semantique)
    if args.comparer:
        comparer({"BM25": lexicale, "Sémantique": semantique, "Hybride": hybride}, charger(CAS))
    else:
        for passage, score in hybride.chercher(args.question):
            print(f"{passage['id']} | {score:.4f} | {passage['titre']} | {passage['url']}")


if __name__ == "__main__":
    main()
