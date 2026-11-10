import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from streamlit.testing.v1 import AppTest

from src.recherche import PASSAGES, charger
from src.reponse import Assistant

PAGE = Path(__file__).resolve().parents[1] / "ui/app.py"


class TestInterface(unittest.TestCase):
    def soumettre(self, question):
        page = AppTest.from_file(str(PAGE)).run()
        page.text_area[0].input(question)
        return page.button[0].click().run()

    def test_question_vide(self):
        with patch("httpx.post") as appel:
            page = self.soumettre("   ")
        appel.assert_not_called()
        self.assertEqual(page.warning[0].value, "Saisis une question.")

    def test_reponse_et_source(self):
        question = "Quelle est la durée d’essai prévue pour un cadre en CDI ?"
        resultat = Assistant(charger(PASSAGES)).repondre(question)
        retour = httpx.Response(200, json=resultat, request=httpx.Request("POST", "http://test/question"))
        with patch("httpx.post", return_value=retour) as appel:
            page = self.soumettre(question)
        self.assertFalse(page.exception)
        self.assertEqual(appel.call_args.kwargs["json"], {"question": question})
        self.assertEqual(page.subheader[0].value, "Réponse")
        self.assertTrue(any(item.label.startswith("Article 14") for item in page.expander))
        self.assertEqual(page.get("link_button")[0].proto.url, resultat["sources"][0]["url"])

    def test_clarification(self):
        question = "Je démissionne de mon CDI. Combien de temps dure mon préavis ?"
        resultat = Assistant(charger(PASSAGES)).repondre(question)
        retour = httpx.Response(200, json=resultat, request=httpx.Request("POST", "http://test/question"))
        with patch("httpx.post", return_value=retour):
            page = self.soumettre(question)
        self.assertFalse(page.exception)
        self.assertEqual(page.subheader[0].value, "Une précision est nécessaire")

    def test_api_injoignable(self):
        with patch("httpx.post", side_effect=httpx.ConnectError("Connexion refusée")):
            page = self.soumettre("Quel est mon préavis ?")
        self.assertIn("Impossible de joindre l’API", page.error[0].value)
