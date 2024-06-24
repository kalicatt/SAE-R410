# Utilisez une image de base Python
FROM python:3.9-slim

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le conteneur au répertoire de travail
COPY requirements.txt .

# Installez les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copiez tout le contenu de votre projet dans le répertoire de travail du conteneur
COPY . .

# Exposez le port sur lequel votre application s'exécute
EXPOSE 8000

# Commande pour exécuter l'application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
