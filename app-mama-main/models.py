# models.py ────────────────────────────────────────────────
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sqlmodel import (
    SQLModel, Field, create_engine, Session,
    Relationship, select
)
import sqlite3, json


DB_FILE = Path("verbs.db")
engine  = create_engine(f"sqlite:///{DB_FILE}", echo=False)


# ────── Modèles ───────────────────────────────────────────
class Verb(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    infinitive: str
    past: str
    past_participle: str
    fr: str

    results: List["Result"] = Relationship(back_populates="verb")


class Result(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    verb_id: int  = Field(foreign_key="verb.id")
    success: bool
    pseudo: str = "guest"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    verb: Optional[Verb] = Relationship(back_populates="results")


# ────── Init BD + auto‑upgrade ────────────────────────────
def init_db(json_path: str = "irregular_verbs.json") -> None:
    """
    • Crée les tables si absentes
    • Ajoute la colonne `pseudo` si manquante (sécurisé multi‑process)
    • Importe le JSON si la table Verb est vide
    """
    SQLModel.metadata.create_all(engine)

    # --- Upgrade : colonne pseudo ---------------------------------------
    with sqlite3.connect(DB_FILE) as raw:
        cols = [row[1] for row in raw.execute("PRAGMA table_info(result);")]
        if "pseudo" not in cols:
            try:
                raw.execute(
                    "ALTER TABLE result ADD COLUMN pseudo TEXT DEFAULT 'guest';"
                )
                raw.commit()
                print("🛠️  Colonne 'pseudo' ajoutée")
            except sqlite3.OperationalError as e:
                # Si un autre processus l’a déjà ajoutée, on ignore
                if "duplicate column name" not in str(e).lower():
                    raise

    # --- Importation des verbes ----------------------------------------
    with Session(engine) as sess:
        nb_verbs = len(sess.exec(select(Verb)).all())
        if nb_verbs == 0:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            sess.add_all(Verb(**v) for v in data)
            sess.commit()
            print(f"✅  {len(data)} verbes importés")
        else:
            print(f"ℹ️  {nb_verbs} verbes déjà présents")
