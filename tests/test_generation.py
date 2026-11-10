import unittest
from unittest.mock import patch

import httpx

from src.generation import AssistantGeneratif, Citation, SortieModele
from src.recherche import PASSAGES, charger


PASSAGE = {
    "id": "code:235", "article": "235", "titre": "Maladie pendant les congés",
    "url": "https://example.org/code.pdf#page=89", "nature": "article_extrait",
    "texte": "Premier paragraphe. Le décompte des jours est décrit dans ce paragraphe.",
    "resume": "Décompte du congé annuel pendant la maladie.", "page_pdf": 17,
}


class TestGeneration(unittest.TestCase):
    def setUp(self):
        self.assistant = AssistantGeneratif([PASSAGE], "modele-test")

    def test_citation_exacte(self):
        extrait = "Le décompte des jours est décrit dans ce paragraphe."
        sortie = SortieModele(statut="repondre", message="Voici la règle.", citations=[
            Citation(id="code:235", extrait=extrait),
        ])
        with patch("src.generation.generer_ollama", return_value=sortie):
            resultat = self.assistant.repondre("Comment décompter la maladie pendant les congés annuels ?")
        self.assertEqual(resultat["statut"], "repondre")
        self.assertEqual(resultat["sources"][0]["texte"], extrait)
        self.assertEqual(resultat["sources"][0]["url"], PASSAGE["url"])

    def test_rejette_reponse_sans_preuve_verifiable(self):
        for citations in (
            [],
            [Citation(id="code:999", extrait=PASSAGE["texte"])],
            [Citation(id="code:235", extrait="Un extrait inventé qui ne figure pas dans le document.")],
        ):
            with self.subTest(citations=citations):
                sortie = SortieModele(statut="repondre", message="À rejeter.", citations=citations)
                with patch("src.generation.generer_ollama", return_value=sortie):
                    with self.assertLogs("src.generation", level="WARNING"):
                        resultat = self.assistant.repondre("Comment décompter la maladie pendant les congés annuels ?")
                self.assertEqual(resultat["statut"], "source_insuffisante")
                self.assertEqual(resultat["sources"], [])

    def test_preavis_utilise_les_regles_meme_en_mode_generatif(self):
        assistant = AssistantGeneratif(charger(PASSAGES), "modele-test")
        with patch("src.generation.generer_ollama") as generer:
            incomplet = assistant.repondre("Je suis cadre en CDI et je veux partir.")
            complet = assistant.repondre("Je quitte mon CDI après huit mois comme employé.")
        generer.assert_not_called()
        self.assertEqual(incomplet["statut"], "clarifier")
        self.assertIn("ancienneté", incomplet["message"])
        self.assertEqual(complet["statut"], "repondre")
        self.assertIn("8 jours", complet["message"])

    def test_modele_injoignable(self):
        with patch("src.generation.generer_ollama", side_effect=httpx.ConnectError("indisponible")):
            with self.assertLogs("src.generation", level="WARNING"):
                resultat = self.assistant.repondre("Comment décompter la maladie pendant les congés annuels ?")
        self.assertEqual(resultat["statut"], "source_insuffisante")
        self.assertIn("indisponible", resultat["message"])
