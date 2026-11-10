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

    def test_preavis_selectionne_la_bonne_ligne_et_tranche(self):
        for categorie, duree, attendu in (
            ("cadre", "11 mois", "1 mois"),
            ("cadre", "12 mois", "2 mois"),
            ("cadre", "cinq ans", "2 mois"),
            ("cadre", "61 mois", "3 mois"),
            ("employée", "huit mois", "8 jours"),
            ("ouvrière", "61 mois", "2 mois"),
        ):
            with self.subTest(categorie=categorie, duree=duree):
                resultat = self.assistant.repondre(
                    f"Je quitte mon CDI après {duree} comme {categorie}. Je dois rester combien de temps ?"
                )
                self.assertEqual(resultat["statut"], "repondre")
                self.assertIn(f"est de {attendu} selon le décret", resultat["message"])
                self.assertEqual({s["id"] for s in resultat["sources"]}, {"code:43", "decret:1"})

    def test_preavis_demande_uniquement_la_precision_manquante(self):
        resultat = self.assistant.repondre("Je suis cadre en CDI et je veux partir. J’ai 25 ans.")
        self.assertEqual(resultat["statut"], "clarifier")
        self.assertIn("ancienneté", resultat["message"])
        self.assertNotIn("catégorie", resultat["message"])
        self.assertNotIn("bareme", resultat)
        resultat = self.assistant.repondre("Je quitte mon CDI après huit mois. Quel est mon préavis ?")
        self.assertEqual(resultat["statut"], "clarifier")
        self.assertIn("catégorie", resultat["message"])
        self.assertNotIn("ancienneté", resultat["message"])

    def test_bareme_identifie_comme_structure(self):
        resultat = self.assistant.repondre(
            "Quel barème de préavis s’applique à un cadre en CDI avec deux ans d’ancienneté ?"
        )
        source = next(s for s in resultat["sources"] if s["id"] == "decret:1")
        self.assertEqual(source["nature"], "bareme_structure")
        self.assertEqual(len(resultat["bareme"]), 2)
