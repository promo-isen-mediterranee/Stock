### Utilisation

Aller dans le dossier DB Init, et avec docker en marche, executer la commande:

`docker compose up --build`

### Installation

Pour utiliser cet API, vous devez:
1) Télécharger ce répertoire.
2) Créer un environnement virtuel: `python3 -m venv .venv`
3) Activer l'environnement `. .venv/bin/activate` sur Linux et MacOS, `. .venv/Scripts/activate` sur Windows.
4) Télécharger les extensions nécessaires en faisant la commande suivante: `pip install -e .`
5) Exécuter le programme en installant un serveur WSGI ou directement en exécutant flask: `flask --app stock run` (attention, la dernière option ne marche que pour un mode développement. Pour la production, veuillez vous reporter à l'utilisation d'un serveur WSGI)
