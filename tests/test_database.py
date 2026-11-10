"""
Tests unitaires pour la couche Database (SQLite en mémoire).
"""

import pytest
from database import Database, DatabaseError
from models import Livre, Emprunt


@pytest.fixture
def db(tmp_path):
    """Base de données temporaire pour chaque test."""
    db_path = tmp_path / "test.db"
    return Database(str(db_path))


class TestDatabaseLivres:
    def test_ajouter_et_obtenir_livre(self, db):
        livre = Livre(titre="Le Petit Prince", auteur="Saint-Exupéry", isbn="978-1", annee=1943, quantite_totale=2, quantite_disponible=2)
        livre_id = db.ajouter_livre(livre)
        assert livre_id is not None

        recupere = db.obtenir_livre(livre_id)
        assert recupere is not None
        assert recupere.titre == "Le Petit Prince"
        assert recupere.isbn == "978-1"

    def test_ajouter_isbn_doublon(self, db):
        livre1 = Livre(titre="Livre 1", auteur="A", isbn="ISBN-UNIQUE", annee=2000, quantite_totale=1, quantite_disponible=1)
        db.ajouter_livre(livre1)

        livre2 = Livre(titre="Livre 2", auteur="B", isbn="ISBN-UNIQUE", annee=2001, quantite_totale=1, quantite_disponible=1)
        with pytest.raises(DatabaseError, match="existe déjà"):
            db.ajouter_livre(livre2)

    def test_rechercher_livres(self, db):
        db.ajouter_livre(Livre(titre="Python Crash Course", auteur="Matthes", isbn="111", annee=2019, quantite_totale=1, quantite_disponible=1))
        db.ajouter_livre(Livre(titre="Clean Code", auteur="Martin", isbn="222", annee=2008, quantite_totale=1, quantite_disponible=1))

        resultats = db.rechercher_livres("python")
        assert len(resultats) == 1
        assert resultats[0].titre == "Python Crash Course"

        tous = db.rechercher_livres()
        assert len(tous) == 2

    def test_modifier_livre(self, db):
        livre_id = db.ajouter_livre(Livre(titre="Ancien", auteur="Auteur", isbn="333", annee=2010, quantite_totale=1, quantite_disponible=1))
        livre = db.obtenir_livre(livre_id)
        livre.titre = "Nouveau titre"
        db.modifier_livre(livre)

        mis_a_jour = db.obtenir_livre(livre_id)
        assert mis_a_jour.titre == "Nouveau titre"

    def test_supprimer_livre(self, db):
        livre_id = db.ajouter_livre(Livre(titre="À supprimer", auteur="X", isbn="444", annee=2020, quantite_totale=1, quantite_disponible=1))
        db.supprimer_livre(livre_id)
        assert db.obtenir_livre(livre_id) is None

    def test_supprimer_livre_avec_emprunt_en_cours(self, db):
        livre_id = db.ajouter_livre(Livre(titre="Emprunté", auteur="Y", isbn="555", annee=2021, quantite_totale=1, quantite_disponible=0))
        db.ajouter_emprunt(Emprunt(livre_id=livre_id, emprunteur="Test"))
        with pytest.raises(DatabaseError, match="emprunts sont encore en cours"):
            db.supprimer_livre(livre_id)


class TestDatabaseEmprunts:
    def test_ajouter_et_lister_emprunts(self, db):
        livre_id = db.ajouter_livre(Livre(titre="Livre", auteur="A", isbn="666", annee=2022, quantite_totale=1, quantite_disponible=1))
        emprunt = Emprunt(livre_id=livre_id, emprunteur="Alice")
        emprunt_id = db.ajouter_emprunt(emprunt)
        assert emprunt_id is not None

        emprunts = db.lister_emprunts()
        assert len(emprunts) == 1
        assert emprunts[0].emprunteur == "Alice"

    def test_lister_par_statut(self, db):
        livre_id = db.ajouter_livre(Livre(titre="Livre", auteur="A", isbn="777", annee=2022, quantite_totale=2, quantite_disponible=2))
        e1 = Emprunt(livre_id=livre_id, emprunteur="A")
        e1_id = db.ajouter_emprunt(e1)
        e2 = Emprunt(livre_id=livre_id, emprunteur="B")
        e2_id = db.ajouter_emprunt(e2)

        e1 = db.obtenir_emprunt(e1_id)
        e1.marquer_retourne()
        db.modifier_emprunt(e1)

        en_cours = db.lister_emprunts(statut="en_cours")
        assert len(en_cours) == 1
        assert en_cours[0].emprunteur == "B"
