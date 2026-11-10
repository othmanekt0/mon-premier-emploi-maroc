"""Prépare les passages du Code à partir du PDF référencé dans le catalogue."""

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = re.compile(r"^[ \t]*Article[ \t]+(\d+)[ \t]*$", re.MULTILINE | re.IGNORECASE)
FOOTER = re.compile(r"^[ \t]*-\s*\d+\s*-[ \t]*$")
SECTION = re.compile(r"^\s*(?:Section|Chapitre|Titre|Livre)\s", re.IGNORECASE)
# Pages PDF, numérotées à partir de 1, dans l'édition référencée sur Adala.
PLAGES = ((17, 32), (88, 91))


def extraire_code(pdf: Path, articles: set[str]) -> dict[str, dict]:
    lecteur = PdfReader(pdf)
    resultats = {}
    for debut, fin in PLAGES:
        morceaux = []
        positions = []
        position = 0
        for numero in range(debut, fin + 1):
            lignes = lecteur.pages[numero - 1].extract_text(extraction_mode="layout").splitlines()
            texte = "\n".join(
                ligne for ligne in lignes
                if not FOOTER.fullmatch(ligne)
                and "Ministère de la Justice" not in ligne
            ) + "\n"
            positions.append((position, numero))
            morceaux.append(texte)
            position += len(texte)

        texte = "".join(morceaux)
        titres = list(ARTICLE.finditer(texte))
        for titre, suivant in zip(titres, titres[1:]):
            article = titre[1]
            if article not in articles:
                continue
            if article in resultats:
                raise ValueError(f"Article {article} extrait plusieurs fois")
            lignes = []
            for ligne in texte[titre.end():suivant.start()].splitlines():
                if SECTION.match(ligne):
                    break
                if ligne.strip():
                    lignes.append(ligne.strip())
            page = max(numero for offset, numero in positions if offset <= titre.start())
            if not lignes:
                raise ValueError(f"Article {article} sans contenu")
            resultats[article] = {"texte": "\n".join(lignes), "page_pdf": page}

    manquants = articles - resultats.keys()
    if manquants:
        raise ValueError(f"Articles introuvables dans cette édition : {sorted(manquants)}")
    return resultats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", required=True, type=Path, help="PDF du Code du travail sur Adala")
    parser.add_argument("--sortie", type=Path, default=ROOT / "data/index/passages.json")
    args = parser.parse_args()
    catalogue = json.loads((ROOT / "data/corpus.json").read_text(encoding="utf-8"))
    articles = {e["article"] for e in catalogue["entrees"] if e["source"] == "code"}
    extraits = extraire_code(args.code, articles)
    passages = []
    for entree in catalogue["entrees"]:
        source, article = entree["source"], entree["article"]
        url = catalogue["sources"][source]["url"]
        passage = {
            **entree,
            "id": f"{source}:{article}",
            "url": url,
            "nature": "article_extrait" if source == "code" else "bareme_structure",
        }
        if source == "code":
            passage.update(extraits[article])
            passage["url"] = f"{url}#page={passage['page_pdf']}"
        else:
            passage.update(json.loads((ROOT / "data/bareme_preavis.json").read_text(encoding="utf-8")))
        passages.append(passage)

    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(passages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(passages)} passages écrits dans {args.sortie}")


if __name__ == "__main__":
    main()
