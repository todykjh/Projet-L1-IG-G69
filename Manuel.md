# Gestionnaire de Bibliothèque (Application Console)

Application console de gestion de bibliothèque réalisée en Python.

## Fonctionnalités

- **Gestion des livres** : ajout, recherche, modification, suppression
- **Emprunts / Retours** : enregistrement des emprunts et des retours avec historique
- **Persistance** : base de données SQLite
- **Export** : export des livres et des emprunts au format CSV
- **Gestion des erreurs** : messages clairs en cas de problème (ISBN déjà existant, livre non disponible, etc.)

## Notions couvertes

- Fonctions et modules
- Structures de données (`dataclass`)
- Programmation orientée objet de base
- SQLite (création de tables, CRUD, contraintes)
- Gestion des erreurs (exceptions personnalisées)
- Tests unitaires avec **pytest**

## Structure du projet

```
bibliotheque/
├── main.py              # Point d'entrée
├── models.py            # Classes Livre et Emprunt
├── database.py          # Accès SQLite
├── services.py          # Logique métier
├── ui.py                # Interface console
├── requirements.txt
├── README.md
└── tests/
    ├── test_models.py
    ├── test_database.py
    └── test_services.py
```

## Installation

```bash
cd bibliotheque
pip install -r requirements.txt
```

## Lancement de l'application

```bash
python main.py
```

## Utilisation (manuel)

Au démarrage, un menu s'affiche :

```
1. Ajouter un livre
2. Rechercher des livres
3. Modifier un livre
4. Supprimer un livre
5. Emprunter un livre
6. Retourner un livre
7. Historique des emprunts
8. Exporter en CSV
0. Quitter
```

### Exemples d'utilisation

**Ajouter un livre**

1. Choisir `1`
2. Saisir titre, auteur, ISBN, année et quantité

**Rechercher**

1. Choisir `2`
2. Entrer un mot-clé (titre, auteur ou ISBN) ou laisser vide pour tout afficher

**Emprunter**

1. Choisir `5`
2. Indiquer l'ID du livre et le nom de l'emprunteur

**Retourner**

1. Choisir `6`
2. Indiquer l'ID de l'emprunt (visible dans l'historique)

**Exporter**

1. Choisir `8`
2. Sélectionner livres ou emprunts → fichiers `livres_export.csv` / `emprunts_export.csv` créés

## Lancer les tests

```bash
cd bibliotheque
pytest -v
```

Les tests utilisent une base SQLite temporaire (aucune pollution de la base réelle).

## Base de données

Le fichier `bibliotheque.db` est créé automatiquement au premier lancement dans le répertoire de travail.

Tables :

- `livres` : id, titre, auteur, isbn (unique), annee, quantite_totale, quantite_disponible
- `emprunts` : id, livre_id, emprunteur, date_emprunt, date_retour, statut

## Auteur

ENI L1 IG Groupe 69 – Gestionnaire de bibliothèque console.

```

```
