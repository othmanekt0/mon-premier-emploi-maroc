"""Mesure la recherche et la réponse sur les questions d’évaluation."""

import argparse
from pathlib import Path

from src.recherche import PASSAGES, charger
from src.reponse import Assistant

CAS = Path(__file__).resolve().parents[1] / "tests/cas_evaluation.json"


def evaluer(assistant, cas):
    mesures = {"recherche": 0, "statut": 0, "citations": 0, "cibles": 0}
    for exemple in cas:
        attendues = set(exemple["references"])
        question = exemple["question"]
        resultat = assistant.repondre(question)
        statut_ok = resultat["statut"] == exemple["statut"]
        mesures["statut"] += statut_ok
        if attendues:
            mesures["cibles"] += 1
            candidats = {p["id"] for p, _ in assistant.recherche.chercher(question)}
            citees = {source["id"] for source in resultat["sources"]}
            mesures["recherche"] += attendues <= candidats
            mesures["citations"] += attendues <= citees

        print(f"{exemple['id']} | statut attendu : {exemple['statut']} | obtenu : {resultat['statut']}")
        print(f"  Critère de lecture : {exemple['critere']}")
        print(f"  Réponse : {resultat['message']}")
        print(f"  Sources : {', '.join(s['id'] for s in resultat['sources']) or 'aucune'}")
        if "bareme" in resultat:
            print(f"  Barème : {resultat['bareme']}")

    print(f"Statuts corrects : {mesures['statut']}/{len(cas)}")
    print(f"Toutes les références retrouvées parmi les cinq premiers : {mesures['recherche']}/{mesures['cibles']}")
    print(f"Toutes les références présentes dans la réponse : {mesures['citations']}/{mesures['cibles']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passages", type=Path, default=PASSAGES)
    parser.add_argument("--jeu", type=Path, default=CAS)
    parser.add_argument("--ollama", metavar="MODELE")
    args = parser.parse_args()
    if not args.passages.is_file():
        parser.error("Passages introuvables. Lancez d’abord src/preparer_passages.py.")
    passages = charger(args.passages)
    if args.ollama:
        from src.generation import AssistantGeneratif

        assistant = AssistantGeneratif(passages, args.ollama)
    else:
        assistant = Assistant(passages)
    evaluer(assistant, charger(args.jeu))


if __name__ == "__main__":
    main()
