"""
Tests unitaires pour la couche Services.
"""

import csv
import os
import pytest
from database import Database
from services import BibliothequeService, ServiceError


@pytest.fixture
def service(tmp_path):
    """Service avec une base de données temporaire."""
    db_path = tmp_path / "test_service.db"
    db = Database(str(db_path))
    return BibliothequeService(db)


class TestBibliothequeServiceLivres:
    def test_ajouter_livre_valide(self, service):
        livre = service.ajouter_livre("Titre", "Auteur", "ISBN-001", 2020, 3)
        assert livre.id is not None
        assert livre.quantite_disponible == 3

    def test_ajouter_livre_titre_vide(self, service):
        with pytest.raises(ServiceError, match="titre est obligatoire"):
            service.ajouter_livre("", "Auteur", "ISBN", 2020)

    def test_ajouter_livre_isbn_doublon(self, service):
        service.ajouter_livre("Livre 1", "A", "ISBN-DUP", 2020)
        with pytest.raises(ServiceError, match="existe déjà"):
            service.ajouter_livre("Livre 2", "B", "ISBN-DUP", 2021)

    def test_rechercher_et_obtenir(self, service):
        service.ajouter_livre("Python", "Matthes", "PY-1", 2019)
        resultats = service.rechercher_livres("python")
        assert len(resultats) == 1

        livre = service.obtenir_livre(resultats[0].id)
        assert livre.titre == "Python"

    def test_obtenir_livre_inexistant(self, service):
        with pytest.raises(ServiceError, match="Aucun livre trouvé"):
            service.obtenir_livre(9999)

    def test_modifier_livre(self, service):
        livre = service.ajouter_livre("Ancien", "Auteur", "MOD-1", 2015)
        modifie = service.modifier_livre(livre.id, titre="Nouveau titre")
        assert modifie.titre == "Nouveau titre"

    def test_supprimer_livre(self, service):
        livre = service.ajouter_livre("À supprimer", "X", "SUP-1", 2020)
        service.supprimer_livre(livre.id)
        with pytest.raises(ServiceError):
            service.obtenir_livre(livre.id)


class TestBibliothequeServiceEmprunts:
    def test_emprunter_et_retourner(self, service):
        livre = service.ajouter_livre("Empruntable", "Auteur", "EMP-1", 2021, quantite=2)
        emprunt = service.emprunter_livre(livre.id, "Alice")
        assert emprunt.statut == "en_cours"

        livre_maj = service.obtenir_livre(livre.id)
        assert livre_maj.quantite_disponible == 1

        retourne = service.retourner_livre(emprunt.id)
        assert retourne.statut == "retourne"

        livre_final = service.obtenir_livre(livre.id)
        assert livre_final.quantite_disponible == 2

    def test_emprunter_non_disponible(self, service):
        livre = service.ajouter_livre("Unique", "Auteur", "EMP-2", 2022, quantite=1)
        service.emprunter_livre(livre.id, "Bob")
        with pytest.raises(ServiceError, match="Aucun exemplaire disponible"):
            service.emprunter_livre(livre.id, "Charlie")

    def test_retourner_deja_retourne(self, service):
        livre = service.ajouter_livre("Livre", "A", "EMP-3", 2020)
        emprunt = service.emprunter_livre(livre.id, "Dave")
        service.retourner_livre(emprunt.id)
        with pytest.raises(ServiceError, match="déjà été retourné"):
            service.retourner_livre(emprunt.id)

    def test_historique(self, service):
        livre = service.ajouter_livre("Histo", "A", "HIST-1", 2018)
        service.emprunter_livre(livre.id, "Eve")
        historique = service.historique_emprunts()
        assert len(historique) == 1
        assert historique[0].emprunteur == "Eve"


class TestExportCSV:
    def test_exporter_livres(self, service, tmp_path):
        service.ajouter_livre("Export", "Auteur", "CSV-1", 2023)
        chemin = str(tmp_path / "livres.csv")
        result = service.exporter_livres_csv(chemin)
        assert os.path.exists(result)

        with open(result, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["titre"] == "Export"

    def test_exporter_vide(self, service):
        with pytest.raises(ServiceError, match="Aucun livre à exporter"):
            service.exporter_livres_csv()
