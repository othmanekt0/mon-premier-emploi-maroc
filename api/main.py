"""API HTTP de l’assistant documentaire."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Request
from pydantic import BaseModel, StringConstraints

from src.generation import AssistantGeneratif
from src.recherche import PASSAGES, charger
from src.reponse import Assistant


class Question(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class Source(BaseModel):
    id: str
    article: str
    titre: str
    url: str
    nature: Literal["article_extrait", "bareme_structure"]
    texte: str
    page_pdf: int


class Reponse(BaseModel):
    statut: Literal["repondre", "clarifier", "hors_perimetre", "source_insuffisante"]
    message: str
    sources: list[Source]
    bareme: list[dict[str, str]] | None = None


def creer_app(chemin_passages: Path = PASSAGES) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if not chemin_passages.is_file():
            raise FileNotFoundError(
                f"Passages introuvables dans {chemin_passages}. "
                "Lancez d’abord src/preparer_passages.py."
            )
        passages = charger(chemin_passages)
        modele = os.environ.get("OLLAMA_MODEL", "").strip()
        app.state.assistant = (
            AssistantGeneratif(passages, modele) if modele else Assistant(passages)
        )
        app.state.nombre_passages = len(passages)
        yield

    app = FastAPI(title="Mon premier emploi au Maroc", lifespan=lifespan)

    @app.get("/health")
    def health(request: Request):
        return {"status": "OK", "passages": request.app.state.nombre_passages}

    @app.post("/question", response_model=Reponse, response_model_exclude_none=True)
    def poser_question(question: Question, request: Request):
        return request.app.state.assistant.repondre(question.question)

    return app


app = creer_app()
