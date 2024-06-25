Projet SAE

Pour pouvoir lancer les différents services il vous faudra :

- Vous rendre dans le fichier cmd et executer la commande pour cree le conteneur NATS
- Vous rendre dans le projet Aeroport_project et executer la commande **docker-compose up --build**
- Vous rendre dans le projet Frontend et executer la commande  **docker-compose up --build**
- Vous rendre dans le fichier database et executer la commande **docker-compose up --build**


Pour pouvoir utiliser correctement la database nous vous recommandons d'effectuer les commandes "**makemigrations** & **migrate**" dans chacun des conteneur projet pour pouvoir avoir accès a toutes les tables.



En dernier lieu, il faudra vous rendre dans le fichier service et executer le script run_nats.py, uqi activeras tout les micros services



En fonction de votre configuration, les parametres de connexion a la base de données, notamment dans les fichier **settings.py** doivent être changer (adpater a votre configuration), pour pouvoir fonctionner correctement.

En fonction de votre configuration, certains paramètres des conteneur peuvent aussi changer (entre windows et mac), adpatez a votre configuration, notamment les adressages ou certaines logiques.




Pour toutes questions n'hesitez pas a nous contacter.
