import unittest
from unittest.mock import patch

import httpx

from src.generation import AssistantGeneratif, Citation, SortieModele


PASSAGE = {
    "id": "code:14", "article": "14", "titre": "Période d’essai",
    "url": "https://example.org/code.pdf#page=17", "nature": "article_extrait",
    "texte": "Premier paragraphe. La durée initiale de cette période est indiquée ici.",
    "resume": "Durée de la période d’essai.", "page_pdf": 17,
}


class TestGeneration(unittest.TestCase):
    def setUp(self):
        self.assistant = AssistantGeneratif([PASSAGE], "modele-test")

    def test_citation_exacte(self):
        extrait = "La durée initiale de cette période est indiquée ici."
        sortie = SortieModele(statut="repondre", message="Voici la règle.", citations=[
            Citation(id="code:14", extrait=extrait),
        ])
        with patch("src.generation.generer_ollama", return_value=sortie):
            resultat = self.assistant.repondre("Quelle est la durée de l’essai ?")
        self.assertEqual(resultat["statut"], "repondre")
        self.assertEqual(resultat["sources"][0]["texte"], extrait)
        self.assertEqual(resultat["sources"][0]["url"], PASSAGE["url"])

    def test_rejette_reponse_sans_preuve_verifiable(self):
        for citations in (
            [],
            [Citation(id="code:999", extrait=PASSAGE["texte"])],
            [Citation(id="code:14", extrait="Un extrait inventé qui ne figure pas dans le document.")],
        ):
            with self.subTest(citations=citations):
                sortie = SortieModele(statut="repondre", message="À rejeter.", citations=citations)
                with patch("src.generation.generer_ollama", return_value=sortie):
                    with self.assertLogs("src.generation", level="WARNING"):
                        resultat = self.assistant.repondre("Quelle est la durée de l’essai ?")
                self.assertEqual(resultat["statut"], "source_insuffisante")
                self.assertEqual(resultat["sources"], [])

    def test_modele_injoignable(self):
        with patch("src.generation.generer_ollama", side_effect=httpx.ConnectError("indisponible")):
            with self.assertLogs("src.generation", level="WARNING"):
                resultat = self.assistant.repondre("Quelle est la durée de l’essai ?")
        self.assertEqual(resultat["statut"], "source_insuffisante")
        self.assertIn("indisponible", resultat["message"])
