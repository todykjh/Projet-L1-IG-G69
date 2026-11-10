"""
Tests unitaires pour les modèles (Livre et Emprunt).
"""

import pytest
from models import Livre, Emprunt


class TestLivre:
    def test_creation_livre(self):
        livre = Livre(titre="1984", auteur="Orwell", isbn="123", annee=1949, quantite_totale=3, quantite_disponible=3)
        assert livre.titre == "1984"
        assert livre.est_disponible() is True

    def test_emprunter_reussi(self):
        livre = Livre(quantite_totale=2, quantite_disponible=2)
        livre.emprunter()
        assert livre.quantite_disponible == 1

    def test_emprunter_echec_plus_disponible(self):
        livre = Livre(quantite_totale=1, quantite_disponible=0)
        with pytest.raises(ValueError, match="Aucun exemplaire disponible"):
            livre.emprunter()

    def test_retourner_reussi(self):
        livre = Livre(quantite_totale=2, quantite_disponible=1)
        livre.retourner()
        assert livre.quantite_disponible == 2

    def test_retourner_echec_deja_complet(self):
        livre = Livre(quantite_totale=2, quantite_disponible=2)
        with pytest.raises(ValueError, match="Tous les exemplaires sont déjà disponibles"):
            livre.retourner()

    def test_to_dict(self):
        livre = Livre(id=1, titre="Test", auteur="Auteur", isbn="ISBN", annee=2020, quantite_totale=1, quantite_disponible=1)
        d = livre.to_dict()
        assert d["id"] == 1
        assert d["titre"] == "Test"
        assert "quantite_disponible" in d


class TestEmprunt:
    def test_creation_emprunt(self):
        emprunt = Emprunt(livre_id=1, emprunteur="Alice")
        assert emprunt.statut == "en_cours"
        assert emprunt.date_retour is None

    def test_marquer_retourne(self):
        emprunt = Emprunt(livre_id=1, emprunteur="Bob")
        emprunt.marquer_retourne()
        assert emprunt.statut == "retourne"
        assert emprunt.date_retour is not None

    def test_marquer_retourne_deux_fois(self):
        emprunt = Emprunt(livre_id=1, emprunteur="Charlie")
        emprunt.marquer_retourne()
        with pytest.raises(ValueError, match="déjà retourné"):
            emprunt.marquer_retourne()

    def test_to_dict(self):
        emprunt = Emprunt(id=5, livre_id=2, emprunteur="Dave")
        d = emprunt.to_dict()
        assert d["id"] == 5
        assert d["emprunteur"] == "Dave"
        assert d["statut"] == "en_cours"
