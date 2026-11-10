import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app, creer_app
from src.recherche import CAS, PASSAGES, charger


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = cls.enterClassContext(TestClient(app))

    def test_sante(self):
        self.assertEqual(self.client.get("/health").json(), {
            "status": "OK", "passages": len(charger(PASSAGES))
        })

    def test_reponses_http(self):
        for cas in charger(CAS):
            with self.subTest(cas=cas["id"]):
                resultat = self.client.post("/question", json={"question": cas["question"]})
                self.assertEqual(resultat.status_code, 200)
                contenu = resultat.json()
                self.assertEqual(contenu["statut"], cas["comportement"])
                self.assertEqual(
                    {source["id"] for source in contenu["sources"]},
                    set(cas["references"]),
                )
                self.assertEqual("bareme" in contenu, (
                    cas["comportement"] == "repondre" and "decret:1" in cas["references"]
                ))

    def test_questions_invalides(self):
        for contenu in ({}, {"question": "  "}, {"question": 42}, {"question": "x" * 2001}):
            with self.subTest(contenu=contenu):
                self.assertEqual(self.client.post("/question", json=contenu).status_code, 422)

    def test_demarrage_sans_corpus(self):
        with tempfile.TemporaryDirectory() as dossier:
            app_sans_corpus = creer_app(Path(dossier) / "absent.json")
            with self.assertRaisesRegex(FileNotFoundError, "Passages introuvables"):
                with TestClient(app_sans_corpus):
                    self.fail("Le démarrage aurait dû échouer.")
