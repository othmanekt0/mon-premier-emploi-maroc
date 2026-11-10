import unittest

from src.recherche import CAS, PASSAGES, charger
from src.reponse import Assistant


class TestReponse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PASSAGES.is_file():
            raise FileNotFoundError("Préparez les passages avec src/preparer_passages.py.")
        cls.passages = charger(PASSAGES)
        cls.assistant = Assistant(cls.passages)

    def test_cas_de_reference(self):
        cas = charger(CAS)
        self.assertEqual(len(cas), 30)
        passages = {p["id"]: p for p in self.passages}
        for exemple in cas:
            with self.subTest(cas=exemple["id"]):
                reponse = self.assistant.repondre(exemple["question"])
                self.assertEqual(reponse["statut"], exemple["comportement"])
                self.assertEqual(
                    {source["id"] for source in reponse["sources"]},
                    set(exemple["references"]),
                )
                for source in reponse["sources"]:
                    self.assertEqual(source["texte"], passages[source["id"]]["texte"])
                    self.assertEqual(source["url"], passages[source["id"]]["url"])
                if reponse["statut"] == "clarifier":
                    self.assertIn("?", reponse["message"])
                    self.assertNotIn("bareme", reponse)

    def test_reference_absente(self):
        passages = [p for p in self.passages if p["id"] != "code:14"]
        resultat = Assistant(passages).repondre("Quelle est la durée d’essai pour un cadre en CDI ?")
        self.assertEqual(resultat["statut"], "source_insuffisante")
        self.assertFalse(resultat["sources"])

    def test_duree_essai_cdi_explicite(self):
        for categorie, duree in (
            ("cadre", "trois mois"),
            ("employée", "un mois et demi"),
            ("ouvrière", "quinze jours"),
        ):
            with self.subTest(categorie=categorie):
                resultat = self.assistant.repondre(
                    f"Quelle est la durée d’essai pour un salarié {categorie} en CDI ?"
                )
                self.assertEqual(resultat["statut"], "repondre")
                self.assertIn(duree, resultat["message"])
                self.assertIn("durée plus courte", resultat["message"])
                self.assertEqual([source["id"] for source in resultat["sources"]], ["code:14"])

    def test_bareme_identifie_comme_structure(self):
        resultat = self.assistant.repondre(
            "Quel barème de préavis s’applique à un cadre en CDI avec deux ans d’ancienneté ?"
        )
        source = next(s for s in resultat["sources"] if s["id"] == "decret:1")
        self.assertEqual(source["nature"], "bareme_structure")
        self.assertEqual(len(resultat["bareme"]), 2)
