"""
FastAPI backend for *Irregular‑Verbs Quiz*

End‑points
──────────
GET  /               → page HTML (index.html)
GET  /quiz?size=25   → liste aléatoire de `size` verbes
POST /answer         → enregistre la réponse d’un·e joueur·se
GET  /progress       → retourne la progression d’un pseudo
POST /reset          → efface la progression d’un pseudo
GET  /verbs          → (optionnel) renvoie tous les verbes
"""

# ── Imports ────────────────────────────────────────────────────────────
from pathlib import Path
from random   import sample, randint
from typing   import List, Optional

from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select

from models import engine, Verb, Result, init_db


# ── Création de l’appli & fichiers statiques ───────────────────────────
app = FastAPI(title="Irregular‑Verbs Quiz API")

# Tous les fichiers dans le dossier ./static
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Page racine (127.0.0.1:8000/)
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(Path("static/index.html"))


# ── Initialisation de la base (création / import JSON) ─────────────────
init_db()   # crée la BD si nécessaire et importe 157 verbes


# ── Dépendance : pseudo transmis dans la query‑string ──────────────────
def get_pseudo(pseudo: str = Query("guest")) -> str:
    """Récupère le pseudo (ou 'guest')."""
    return pseudo.strip() or "guest"


# ── Schémas Pydantic pour les POST ─────────────────────────────────────
class AnswerIn(BaseModel):
    verb_id: int
    user_past: str
    user_participle: str


# ── End‑points ─────────────────────────────────────────────────────────
@app.get("/verbs", response_model=list[Verb])
def list_verbs():
    """Retourne **tous** les verbes (pour debug/adm)."""
    with Session(engine) as sess:
        return sess.exec(select(Verb)).all()


@app.get("/quiz", response_model=list[Verb])
def quiz(size: Optional[int] = Query(None, ge=1, le=200)):
    """
    Renvoie une liste aléatoire de *size* verbes.
    - Si *size* omis ⇒ tirage aléatoire entre 5 et 25.
    """
    size = size or randint(5, 25)
    with Session(engine) as sess:
        verbs = sess.exec(select(Verb)).all()

    if len(verbs) < size:
        raise HTTPException(400, "Pas assez de verbes en base.")
    return sample(verbs, k=size)


@app.post("/answer")
def answer(data: AnswerIn, pseudo: str = Depends(get_pseudo)):
    """
    Enregistre la réponse et retourne si elle est correcte ou non.
    """
    with Session(engine) as sess:
        verb = sess.get(Verb, data.verb_id)
        if not verb:
            raise HTTPException(404, "Verbe introuvable")

        correct = (
            data.user_past.strip().lower() == verb.past.lower()
            and data.user_participle.strip().lower() == verb.past_participle.lower()
        )

        sess.add(Result(verb_id=verb.id, pseudo=pseudo, success=correct))
        sess.commit()

        return {
            "correct": correct,
            "expected": {
                "past": verb.past,
                "participle": verb.past_participle,
            },
        }


@app.get("/progress")
def progress(pseudo: str = Depends(get_pseudo)):
    """Progression pour *pseudo*."""
    with Session(engine) as sess:
        total   = sess.exec(select(Result).where(Result.pseudo == pseudo)).count()
        success = sess.exec(
            select(Result).where(Result.pseudo == pseudo, Result.success == True)
        ).count()

    return {
        "pseudo" : pseudo,
        "total"  : total,
        "success": success,
        "rate"   : round(success / total * 100, 1) if total else 0.0,
    }


@app.post("/reset")
def reset(pseudo: str = Depends(get_pseudo)):
    """
    Supprime toutes les réponses du pseudo → progression remise à 0.
    """
    with Session(engine) as sess:
        q = select(Result).where(Result.pseudo == pseudo)
        nb = sess.exec(q).count()

        if nb:
            sess.exec(
                select(Result).where(Result.pseudo == pseudo)
                .delete(synchronize_session=False)
            )
            sess.commit()

    return {"deleted": nb}
