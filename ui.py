"""
Interface console du gestionnaire de bibliothèque.
"""

from services import BibliothequeService, ServiceError


class ConsoleUI:
    """Interface utilisateur en mode console."""

    def __init__(self, service: BibliothequeService | None = None):
        self.service = service or BibliothequeService()

    def run(self) -> None:
        """Boucle principale du menu."""
        print("=" * 55)
        print("   GESTIONNAIRE DE BIBLIOTHÈQUE")
        print("=" * 55)

        while True:
            self._afficher_menu()
            choix = input("\nVotre choix : ").strip()

            try:
                if choix == "1":
                    self._ajouter_livre()
                elif choix == "2":
                    self._rechercher_livres()
                elif choix == "3":
                    self._modifier_livre()
                elif choix == "4":
                    self._supprimer_livre()
                elif choix == "5":
                    self._emprunter_livre()
                elif choix == "6":
                    self._retourner_livre()
                elif choix == "7":
                    self._historique_emprunts()
                elif choix == "8":
                    self._exporter_csv()
                elif choix == "0":
                    print("\nAu revoir !")
                    break
                else:
                    print("Choix invalide. Veuillez réessayer.")
            except ServiceError as e:
                print(f"\n❌ Erreur : {e}")
            except KeyboardInterrupt:
                print("\n\nInterruption. Au revoir !")
                break
            except Exception as e:
                print(f"\n❌ Erreur inattendue : {e}")

    def _afficher_menu(self) -> None:
        print("\n" + "-" * 40)
        print("1. Ajouter un livre")
        print("2. Rechercher des livres")
        print("3. Modifier un livre")
        print("4. Supprimer un livre")
        print("5. Emprunter un livre")
        print("6. Retourner un livre")
        print("7. Historique des emprunts")
        print("8. Exporter en CSV")
        print("0. Quitter")
        print("-" * 40)

    def _ajouter_livre(self) -> None:
        print("\n--- Ajouter un livre ---")
        titre = input("Titre : ").strip()
        auteur = input("Auteur : ").strip()
        isbn = input("ISBN : ").strip()
        annee_str = input("Année de publication : ").strip()
        quantite_str = input("Quantité (défaut 1) : ").strip() or "1"

        try:
            annee = int(annee_str)
            quantite = int(quantite_str)
        except ValueError:
            print("❌ Année et quantité doivent être des nombres entiers.")
            return

        livre = self.service.ajouter_livre(titre, auteur, isbn, annee, quantite)
        print(f"\n✅ Livre ajouté avec succès (id = {livre.id})")

    def _rechercher_livres(self) -> None:
        print("\n--- Recherche de livres ---")
        terme = input("Terme de recherche (titre, auteur ou ISBN, vide = tous) : ").strip()
        livres = self.service.rechercher_livres(terme)

        if not livres:
            print("Aucun livre trouvé.")
            return

        print(f"\n{len(livres)} livre(s) trouvé(s) :\n")
        print(f"{'ID':<5} {'Titre':<30} {'Auteur':<20} {'ISBN':<15} {'Disp.':<8} {'Total'}")
        print("-" * 90)
        for l in livres:
            print(
                f"{l.id:<5} {l.titre[:29]:<30} {l.auteur[:19]:<20} "
                f"{l.isbn:<15} {l.quantite_disponible:<8} {l.quantite_totale}"
            )

    def _modifier_livre(self) -> None:
        print("\n--- Modifier un livre ---")
        try:
            livre_id = int(input("ID du livre à modifier : ").strip())
        except ValueError:
            print("❌ ID invalide.")
            return

        livre = self.service.obtenir_livre(livre_id)
        print(f"\nLivre actuel : {livre.titre} – {livre.auteur} (ISBN {livre.isbn})")

        titre = input(f"Nouveau titre [{livre.titre}] : ").strip() or None
        auteur = input(f"Nouvel auteur [{livre.auteur}] : ").strip() or None
        isbn = input(f"Nouvel ISBN [{livre.isbn}] : ").strip() or None
        annee_str = input(f"Nouvelle année [{livre.annee}] : ").strip()
        quantite_str = input(f"Nouvelle quantité totale [{livre.quantite_totale}] : ").strip()

        annee = int(annee_str) if annee_str else None
        quantite = int(quantite_str) if quantite_str else None

        livre = self.service.modifier_livre(
            livre_id, titre=titre, auteur=auteur, isbn=isbn, annee=annee, quantite_totale=quantite
        )
        print(f"\n✅ Livre modifié avec succès.")

    def _supprimer_livre(self) -> None:
        print("\n--- Supprimer un livre ---")
        try:
            livre_id = int(input("ID du livre à supprimer : ").strip())
        except ValueError:
            print("❌ ID invalide.")
            return

        confirmation = input(f"Confirmer la suppression du livre {livre_id} ? (o/n) : ").strip().lower()
        if confirmation != "o":
            print("Suppression annulée.")
            return

        self.service.supprimer_livre(livre_id)
        print("\n✅ Livre supprimé.")

    def _emprunter_livre(self) -> None:
        print("\n--- Emprunter un livre ---")
        try:
            livre_id = int(input("ID du livre : ").strip())
        except ValueError:
            print("❌ ID invalide.")
            return
        emprunteur = input("Nom de l'emprunteur : ").strip()

        emprunt = self.service.emprunter_livre(livre_id, emprunteur)
        print(f"\n✅ Emprunt enregistré (id emprunt = {emprunt.id})")

    def _retourner_livre(self) -> None:
        print("\n--- Retourner un livre ---")
        try:
            emprunt_id = int(input("ID de l'emprunt : ").strip())
        except ValueError:
            print("❌ ID invalide.")
            return

        emprunt = self.service.retourner_livre(emprunt_id)
        print(f"\n✅ Livre retourné (emprunt id = {emprunt.id})")

    def _historique_emprunts(self) -> None:
        print("\n--- Historique des emprunts ---")
        print("1. Tous les emprunts")
        print("2. Emprunts en cours uniquement")
        print("3. Emprunts retournés uniquement")
        sous_choix = input("Votre choix : ").strip()

        statut = None
        if sous_choix == "2":
            statut = "en_cours"
        elif sous_choix == "3":
            statut = "retourne"

        emprunts = self.service.historique_emprunts(statut=statut)
        if not emprunts:
            print("Aucun emprunt trouvé.")
            return

        print(f"\n{len(emprunts)} emprunt(s) :\n")
        print(f"{'ID':<5} {'Livre ID':<10} {'Emprunteur':<20} {'Date emprunt':<20} {'Date retour':<20} {'Statut'}")
        print("-" * 100)
        for e in emprunts:
            date_retour = e.date_retour or "-"
            print(
                f"{e.id:<5} {e.livre_id:<10} {e.emprunteur[:19]:<20} "
                f"{e.date_emprunt:<20} {date_retour:<20} {e.statut}"
            )

    def _exporter_csv(self) -> None:
        print("\n--- Export CSV ---")
        print("1. Exporter les livres")
        print("2. Exporter les emprunts")
        sous_choix = input("Votre choix : ").strip()

        if sous_choix == "1":
            chemin = self.service.exporter_livres_csv()
            print(f"\n✅ Livres exportés dans : {chemin}")
        elif sous_choix == "2":
            chemin = self.service.exporter_emprunts_csv()
            print(f"\n✅ Emprunts exportés dans : {chemin}")
        else:
            print("Choix invalide.")
