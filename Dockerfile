FROM python:3.12


###############################
#  Variables d'environnement  #
###############################

# Base de donnée
ENV DB_HOST=logistisen_db
ENV DB_PORT=5432
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_NAME=logistisen_db
ENV SQLALCHEMY_TRACK_MODIFICATIONS=False

# Flask
ENV FLASK_APP=API_Stock/src/__init__.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050
ENV SESSION_DURATION_SECONDS=900


###############################
#  Configuration de l'image   #
###############################

# Création du répertoire de travail
WORKDIR /API_Stock

# Copie des fichiers de configuration
COPY API_Stock/requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY API_Stock/src /API_Stock/src

# Expose le port 5050
EXPOSE 5050

# Spécifie la commande à exécuter
CMD ["flask", "run"]