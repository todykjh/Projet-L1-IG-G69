#!/usr/bin/env python3
"""
Point d'entrée de l'application Gestionnaire de Bibliothèque.
"""

from ui import ConsoleUI


def main() -> None:
    app = ConsoleUI()
    app.run()


if __name__ == "__main__":
    main()
