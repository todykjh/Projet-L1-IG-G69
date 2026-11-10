"""
Couche de services (logique métier).
"""

import csv
from typing import List, Optional

from database import Database, DatabaseError
from models import Livre, Emprunt


class ServiceError(Exception):
    """Exception métier."""
    pass


class BibliothequeService:
    """Service principal de gestion de la bibliothèque."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    # ---------- Livres ----------

    def ajouter_livre(
        self,
        titre: str,
        auteur: str,
        isbn: str,
        annee: int,
        quantite: int = 1,
    ) -> Livre:
        """Ajoute un nouveau livre."""
        titre = titre.strip()
        auteur = auteur.strip()
        isbn = isbn.strip()

        if not titre:
            raise ServiceError("Le titre est obligatoire.")
        if not auteur:
            raise ServiceError("L'auteur est obligatoire.")
        if not isbn:
            raise ServiceError("L'ISBN est obligatoire.")
        if annee < 0 or annee > 2100:
            raise ServiceError("L'année doit être un nombre valide.")
        if quantite < 1:
            raise ServiceError("La quantité doit être au moins 1.")

        livre = Livre(
            titre=titre,
            auteur=auteur,
            isbn=isbn,
            annee=annee,
            quantite_totale=quantite,
            quantite_disponible=quantite,
        )
        try:
            livre.id = self.db.ajouter_livre(livre)
        except DatabaseError as e:
            raise ServiceError(str(e)) from e
        return livre

    def rechercher_livres(self, terme: str = "") -> List[Livre]:
        """Recherche des livres."""
        return self.db.rechercher_livres(terme)

    def obtenir_livre(self, livre_id: int) -> Livre:
        """Récupère un livre ou lève une exception."""
        livre = self.db.obtenir_livre(livre_id)
        if livre is None:
            raise ServiceError(f"Aucun livre trouvé avec l'id {livre_id}.")
        return livre

    def modifier_livre(
        self,
        livre_id: int,
        titre: Optional[str] = None,
        auteur: Optional[str] = None,
        isbn: Optional[str] = None,
        annee: Optional[int] = None,
        quantite_totale: Optional[int] = None,
    ) -> Livre:
        """Modifie un livre existant."""
        livre = self.obtenir_livre(livre_id)

        if titre is not None:
            titre = titre.strip()
            if not titre:
                raise ServiceError("Le titre ne peut pas être vide.")
            livre.titre = titre
        if auteur is not None:
            auteur = auteur.strip()
            if not auteur:
                raise ServiceError("L'auteur ne peut pas être vide.")
            livre.auteur = auteur
        if isbn is not None:
            isbn = isbn.strip()
            if not isbn:
                raise ServiceError("L'ISBN ne peut pas être vide.")
            livre.isbn = isbn
        if annee is not None:
            if annee < 0 or annee > 2100:
                raise ServiceError("L'année doit être un nombre valide.")
            livre.annee = annee
        if quantite_totale is not None:
            if quantite_totale < 1:
                raise ServiceError("La quantité totale doit être au moins 1.")
            # Ajuster la disponibilité proportionnellement
            empruntes = livre.quantite_totale - livre.quantite_disponible
            if quantite_totale < empruntes:
                raise ServiceError(
                    f"Impossible de réduire la quantité : {empruntes} exemplaire(s) sont déjà empruntés."
                )
            livre.quantite_totale = quantite_totale
            livre.quantite_disponible = quantite_totale - empruntes

        try:
            self.db.modifier_livre(livre)
        except DatabaseError as e:
            raise ServiceError(str(e)) from e
        return livre

    def supprimer_livre(self, livre_id: int) -> None:
        """Supprime un livre."""
        try:
            self.db.supprimer_livre(livre_id)
        except DatabaseError as e:
            raise ServiceError(str(e)) from e

    # ---------- Emprunts ----------

    def emprunter_livre(self, livre_id: int, emprunteur: str) -> Emprunt:
        """Emprunte un livre."""
        emprunteur = emprunteur.strip()
        if not emprunteur:
            raise ServiceError("Le nom de l'emprunteur est obligatoire.")

        livre = self.obtenir_livre(livre_id)
        if not livre.est_disponible():
            raise ServiceError("Aucun exemplaire disponible pour ce livre.")

        try:
            livre.emprunter()
            self.db.mettre_a_jour_disponibilite(livre.id, livre.quantite_disponible)
            emprunt = Emprunt(livre_id=livre.id, emprunteur=emprunteur)
            emprunt.id = self.db.ajouter_emprunt(emprunt)
            return emprunt
        except (DatabaseError, ValueError) as e:
            raise ServiceError(str(e)) from e

    def retourner_livre(self, emprunt_id: int) -> Emprunt:
        """Retourne un livre emprunté."""
        emprunt = self.db.obtenir_emprunt(emprunt_id)
        if emprunt is None:
            raise ServiceError(f"Aucun emprunt trouvé avec l'id {emprunt_id}.")
        if emprunt.statut == "retourne":
            raise ServiceError("Cet emprunt a déjà été retourné.")

        livre = self.obtenir_livre(emprunt.livre_id)
        try:
            livre.retourner()
            self.db.mettre_a_jour_disponibilite(livre.id, livre.quantite_disponible)
            emprunt.marquer_retourne()
            self.db.modifier_emprunt(emprunt)
            return emprunt
        except (DatabaseError, ValueError) as e:
            raise ServiceError(str(e)) from e

    def historique_emprunts(
        self, statut: Optional[str] = None, livre_id: Optional[int] = None
    ) -> List[Emprunt]:
        """Retourne l'historique des emprunts."""
        return self.db.lister_emprunts(statut=statut, livre_id=livre_id)

    # ---------- Export ----------

    def exporter_livres_csv(self, chemin: str = "livres_export.csv") -> str:
        """Exporte tous les livres en CSV."""
        livres = self.rechercher_livres()
        if not livres:
            raise ServiceError("Aucun livre à exporter.")

        with open(chemin, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "titre",
                    "auteur",
                    "isbn",
                    "annee",
                    "quantite_totale",
                    "quantite_disponible",
                ],
            )
            writer.writeheader()
            for livre in livres:
                writer.writerow(livre.to_dict())
        return chemin

    def exporter_emprunts_csv(self, chemin: str = "emprunts_export.csv") -> str:
        """Exporte tous les emprunts en CSV."""
        emprunts = self.historique_emprunts()
        if not emprunts:
            raise ServiceError("Aucun emprunt à exporter.")

        with open(chemin, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "livre_id",
                    "emprunteur",
                    "date_emprunt",
                    "date_retour",
                    "statut",
                ],
            )
            writer.writeheader()
            for emprunt in emprunts:
                writer.writerow(emprunt.to_dict())
        return chemin
