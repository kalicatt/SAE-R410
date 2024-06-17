# Projet Compagnie Aérienne

## Prérequis

Assurez-vous d'avoir les éléments suivants installés sur votre système :
- Python (version 3.8 ou supérieure)
- Docker
- Django (installé via `pip`)
- Serveur NATS

## Configuration du Projet

1. **Cloner le Répertoire**
    ```bash
    git clone https://github.com/votre-nom-utilisateur/Aeroport_project.git
    cd Aeroport_project
    ```

2. **Installer les Dépendances Python**
    ```bash
    pip install -r requirements.txt
    ```

## Exécution du Projet

### Démarrer le Serveur Backend

Ouvrez un terminal, naviguez jusqu'au répertoire du projet, puis exécutez :

```bash
cd Aeroport_project
python manage.py runserver 8002
