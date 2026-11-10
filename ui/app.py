"""Interface de consultation des réponses et des sources."""

import os

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000").rstrip("/")
EXEMPLES = (
    "Quelle est la durée d’essai prévue pour un cadre en CDI ?",
    "À combien de jours de congé annuel ai-je droit ?",
    "Je démissionne de mon CDI. Combien de temps dure mon préavis ?",
)
TITRES = {
    "repondre": "Réponse",
    "clarifier": "Une précision est nécessaire",
    "hors_perimetre": "Question hors périmètre",
    "source_insuffisante": "Source insuffisante",
}


def afficher_reponse(reponse):
    statut = reponse["statut"]
    st.subheader(TITRES[statut])
    st.text(reponse["message"])
    if statut == "clarifier":
        st.caption("Ajoute la précision à ta question, puis envoie-la à nouveau.")
    if reponse.get("bareme"):
        st.table([
            {
                "Catégorie": ligne["categorie"],
                "Moins d’un an": ligne["moins_un_an"],
                "De 1 à 5 ans": ligne["un_a_cinq_ans"],
                "Plus de 5 ans": ligne["plus_de_cinq_ans"],
            }
            for ligne in reponse["bareme"]
        ])
    if reponse["sources"]:
        st.subheader("Sources officielles")
        for source in reponse["sources"]:
            with st.expander(f"Article {source['article']} · {source['titre']}"):
                if source["nature"] == "bareme_structure":
                    st.caption("Barème structuré. Le texte du décret est consultable dans le Bulletin officiel.")
                st.text(source["texte"])
                st.link_button("Ouvrir le document officiel", source["url"])


st.set_page_config(page_title="Mon premier emploi au Maroc")
st.title("Mon premier emploi au Maroc")
st.write("Pose une question sur la période d’essai, les congés annuels payés ou le préavis de démission en CDI.")
with st.expander("Exemples de questions"):
    for exemple in EXEMPLES:
        st.write(exemple)

with st.form("question"):
    question = st.text_area("Ta question", max_chars=2000)
    envoyer = st.form_submit_button("Poser la question")

if envoyer:
    if not question.strip():
        st.warning("Saisis une question.")
    else:
        try:
            with st.spinner("Recherche des sources…"):
                retour = httpx.post(
                    f"{API_URL}/question", json={"question": question.strip()}, timeout=130
                )
                retour.raise_for_status()
                reponse = retour.json()
        except httpx.RequestError:
            st.error("Impossible de joindre l’API. Vérifie qu’elle est démarrée.")
        except (httpx.HTTPStatusError, ValueError):
            st.error("L’API n’a pas pu traiter cette question.")
        else:
            afficher_reponse(reponse)
