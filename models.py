"""
Modèles de données pour le gestionnaire de bibliothèque.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Livre:
    """Représente un livre dans la bibliothèque."""
    id: Optional[int] = None
    titre: str = ""
    auteur: str = ""
    isbn: str = ""
    annee: int = 0
    quantite_totale: int = 1
    quantite_disponible: int = 1

    def est_disponible(self) -> bool:
        """Retourne True si au moins un exemplaire est disponible."""
        return self.quantite_disponible > 0

    def emprunter(self) -> None:
        """Décrémente la quantité disponible."""
        if not self.est_disponible():
            raise ValueError("Aucun exemplaire disponible pour ce livre.")
        self.quantite_disponible -= 1

    def retourner(self) -> None:
        """Incrémente la quantité disponible."""
        if self.quantite_disponible >= self.quantite_totale:
            raise ValueError("Tous les exemplaires sont déjà disponibles.")
        self.quantite_disponible += 1

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire (utile pour CSV)."""
        return {
            "id": self.id,
            "titre": self.titre,
            "auteur": self.auteur,
            "isbn": self.isbn,
            "annee": self.annee,
            "quantite_totale": self.quantite_totale,
            "quantite_disponible": self.quantite_disponible,
        }


@dataclass
class Emprunt:
    """Représente un emprunt de livre."""
    id: Optional[int] = None
    livre_id: int = 0
    emprunteur: str = ""
    date_emprunt: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date_retour: Optional[str] = None
    statut: str = "en_cours"  # "en_cours" ou "retourne"

    def marquer_retourne(self) -> None:
        """Marque l'emprunt comme retourné."""
        if self.statut == "retourne":
            raise ValueError("Cet emprunt est déjà retourné.")
        self.date_retour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.statut = "retourne"

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "livre_id": self.livre_id,
            "emprunteur": self.emprunteur,
            "date_emprunt": self.date_emprunt,
            "date_retour": self.date_retour or "",
            "statut": self.statut,
        }
