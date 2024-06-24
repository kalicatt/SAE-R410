# Utiliser une image de base Python officielle
FROM python:3.9

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu de l'application dans le répertoire de travail du conteneur
COPY . .

# Exposer le port sur lequel l'application s'exécute
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
