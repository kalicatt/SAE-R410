- DEMARRER Aeroport_project : python manage.py runserver 8002
- DEMARRER FRONTEND : python manage.py runserver

- FAIRE sur Aeroport_project : py manage.py run_nats

- NE PAS OUBLIER DE LANCER LE SERVER NATS à l'aide du Dockerfile car il y a une conf de websocket.

FAIRE LES COMMANDES SUR DAUTRES TERMINAUX SINON CA FONCTIONNE PAS LOL


Ce qu'il fonctionne : inscription, connexion, session de connexion, visualisation des vols arrivées et depart.

Ce qui arrive : gestions des vols et payement, réservation.
