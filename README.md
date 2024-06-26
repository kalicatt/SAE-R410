# Projet SAE

## Instructions de déploiement

### Étapes pour lancer les services

1. **Démarrer le conteneur NATS**:
   - Accédez au dossier `cmd` et exécutez la commande pour créer le conteneur NATS.

2. **Démarrer le projet Aeroport**:
   - Accédez au dossier `Aeroport_project` et exécutez la commande :
     ```sh
     docker-compose up --build
     ```

3. **Démarrer le projet Frontend**:
   - Accédez au dossier `Frontend` et exécutez la commande :
     ```sh
     docker-compose up --build
     ```

4. **Démarrer la base de données**:
   - Accédez au dossier `database` et exécutez la commande :
     ```sh
     docker-compose up --build
     ```

### Configuration de la base de données

Pour utiliser correctement la base de données, il est recommandé d'exécuter les commandes `makemigrations` et `migrate` dans chaque conteneur projet pour s'assurer de la création de toutes les tables nécessaires.

### Démarrage des microservices

Pour activer tous les microservices, accédez au dossier `services` et exécutez le script `run_nats.py`.

### Configuration spécifique

- **Paramètres de connexion à la base de données** :
  - Adaptez les paramètres dans le fichier `settings.py` en fonction de votre configuration pour assurer le bon fonctionnement.

- **Paramètres des conteneurs** :
  - En fonction de votre système d'exploitation (Windows ou Mac), certains paramètres des conteneurs peuvent nécessiter des ajustements, notamment les adresses et certaines logiques.

### Support

Pour toute question, n'hésitez pas à nous contacter.
