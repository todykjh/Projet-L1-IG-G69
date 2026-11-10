"""
Gestion de la base de données SQLite.
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Tuple

from models import Livre, Emprunt


class DatabaseError(Exception):
    """Exception personnalisée pour les erreurs de base de données."""
    pass


class Database:
    """Classe responsable de toutes les opérations SQLite."""

    def __init__(self, db_path: str = "bibliotheque.db"):
        self.db_path = db_path
        self._creer_tables()

    @contextmanager
    def _connexion(self):
        """Context manager pour une connexion sécurisée."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur SQLite : {e}") from e
        finally:
            if conn:
                conn.close()

    def _creer_tables(self) -> None:
        """Crée les tables si elles n'existent pas."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS livres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT NOT NULL,
                    auteur TEXT NOT NULL,
                    isbn TEXT UNIQUE NOT NULL,
                    annee INTEGER NOT NULL,
                    quantite_totale INTEGER NOT NULL DEFAULT 1,
                    quantite_disponible INTEGER NOT NULL DEFAULT 1
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emprunts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    livre_id INTEGER NOT NULL,
                    emprunteur TEXT NOT NULL,
                    date_emprunt TEXT NOT NULL,
                    date_retour TEXT,
                    statut TEXT NOT NULL DEFAULT 'en_cours',
                    FOREIGN KEY (livre_id) REFERENCES livres(id)
                )
            """)

    # ---------- Livres ----------

    def ajouter_livre(self, livre: Livre) -> int:
        """Ajoute un livre et retourne son id."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO livres (titre, auteur, isbn, annee, quantite_totale, quantite_disponible)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        livre.titre,
                        livre.auteur,
                        livre.isbn,
                        livre.annee,
                        livre.quantite_totale,
                        livre.quantite_disponible,
                    ),
                )
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise DatabaseError(f"Un livre avec l'ISBN '{livre.isbn}' existe déjà.")

    def obtenir_livre(self, livre_id: int) -> Optional[Livre]:
        """Récupère un livre par son id."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livres WHERE id = ?", (livre_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_livre(row)

    def obtenir_livre_par_isbn(self, isbn: str) -> Optional[Livre]:
        """Récupère un livre par son ISBN."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livres WHERE isbn = ?", (isbn,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_livre(row)

    def rechercher_livres(self, terme: str = "") -> List[Livre]:
        """Recherche des livres par titre ou auteur (insensible à la casse)."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            if terme.strip() == "":
                cursor.execute("SELECT * FROM livres ORDER BY titre")
            else:
                motif = f"%{terme}%"
                cursor.execute(
                    """
                    SELECT * FROM livres
                    WHERE titre LIKE ? OR auteur LIKE ? OR isbn LIKE ?
                    ORDER BY titre
                    """,
                    (motif, motif, motif),
                )
            return [self._row_to_livre(row) for row in cursor.fetchall()]

    def modifier_livre(self, livre: Livre) -> None:
        """Met à jour un livre existant."""
        if livre.id is None:
            raise DatabaseError("Impossible de modifier un livre sans id.")
        with self._connexion() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE livres
                    SET titre = ?, auteur = ?, isbn = ?, annee = ?,
                        quantite_totale = ?, quantite_disponible = ?
                    WHERE id = ?
                    """,
                    (
                        livre.titre,
                        livre.auteur,
                        livre.isbn,
                        livre.annee,
                        livre.quantite_totale,
                        livre.quantite_disponible,
                        livre.id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Aucun livre trouvé avec l'id {livre.id}.")
            except sqlite3.IntegrityError:
                raise DatabaseError(f"Un autre livre utilise déjà l'ISBN '{livre.isbn}'.")

    def supprimer_livre(self, livre_id: int) -> None:
        """Supprime un livre (uniquement s'il n'a pas d'emprunts en cours)."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM emprunts WHERE livre_id = ? AND statut = 'en_cours'",
                (livre_id,),
            )
            if cursor.fetchone()[0] > 0:
                raise DatabaseError(
                    "Impossible de supprimer ce livre : des emprunts sont encore en cours."
                )
            cursor.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
            if cursor.rowcount == 0:
                raise DatabaseError(f"Aucun livre trouvé avec l'id {livre_id}.")

    def mettre_a_jour_disponibilite(self, livre_id: int, quantite_disponible: int) -> None:
        """Met à jour uniquement la quantité disponible."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE livres SET quantite_disponible = ? WHERE id = ?",
                (quantite_disponible, livre_id),
            )
            if cursor.rowcount == 0:
                raise DatabaseError(f"Aucun livre trouvé avec l'id {livre_id}.")

    # ---------- Emprunts ----------

    def ajouter_emprunt(self, emprunt: Emprunt) -> int:
        """Ajoute un emprunt et retourne son id."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO emprunts (livre_id, emprunteur, date_emprunt, date_retour, statut)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    emprunt.livre_id,
                    emprunt.emprunteur,
                    emprunt.date_emprunt,
                    emprunt.date_retour,
                    emprunt.statut,
                ),
            )
            return cursor.lastrowid

    def obtenir_emprunt(self, emprunt_id: int) -> Optional[Emprunt]:
        """Récupère un emprunt par son id."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emprunts WHERE id = ?", (emprunt_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_emprunt(row)

    def lister_emprunts(
        self, statut: Optional[str] = None, livre_id: Optional[int] = None
    ) -> List[Emprunt]:
        """Liste les emprunts, éventuellement filtrés."""
        with self._connexion() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM emprunts WHERE 1=1"
            params: list = []
            if statut is not None:
                query += " AND statut = ?"
                params.append(statut)
            if livre_id is not None:
                query += " AND livre_id = ?"
                params.append(livre_id)
            query += " ORDER BY date_emprunt DESC"
            cursor.execute(query, params)
            return [self._row_to_emprunt(row) for row in cursor.fetchall()]

    def modifier_emprunt(self, emprunt: Emprunt) -> None:
        """Met à jour un emprunt (principalement pour le retour)."""
        if emprunt.id is None:
            raise DatabaseError("Impossible de modifier un emprunt sans id.")
        with self._connexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE emprunts
                SET date_retour = ?, statut = ?
                WHERE id = ?
                """,
                (emprunt.date_retour, emprunt.statut, emprunt.id),
            )
            if cursor.rowcount == 0:
                raise DatabaseError(f"Aucun emprunt trouvé avec l'id {emprunt.id}.")

    # ---------- Helpers ----------

    @staticmethod
    def _row_to_livre(row: sqlite3.Row) -> Livre:
        return Livre(
            id=row["id"],
            titre=row["titre"],
            auteur=row["auteur"],
            isbn=row["isbn"],
            annee=row["annee"],
            quantite_totale=row["quantite_totale"],
            quantite_disponible=row["quantite_disponible"],
        )

    @staticmethod
    def _row_to_emprunt(row: sqlite3.Row) -> Emprunt:
        return Emprunt(
            id=row["id"],
            livre_id=row["livre_id"],
            emprunteur=row["emprunteur"],
            date_emprunt=row["date_emprunt"],
            date_retour=row["date_retour"],
            statut=row["statut"],
        )
