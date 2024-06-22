import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_client_by_id(client_id):
    """
    Obtient les informations d'un client par son ID.

    Args:
        client_id (int): L'ID du client.

    Returns:
        dict: Les données du client si elles existent, None sinon.
    """
    logging.debug(f"Obtention du client par ID : {client_id}")
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/{client_id}/'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Données du client pour l'ID {client_id} : {data}")
                return data
            logging.error(f"Échec de l'obtention du client pour l'ID {client_id}, code de statut : {response.status}")
            return None

async def create_reservation(user_email, flight_id):
    """
    Crée une réservation pour un client donné et un vol donné.

    Args:
        user_email (str): L'email de l'utilisateur.
        flight_id (int): L'ID du vol.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données du client par email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Échec de la récupération des données du client pour l'email {user_email}")
                return {'status': 'error', 'message': f'Client avec l email {user_email} n existe pas'}
            client_data = await client_response.json()
            if not client_data:
                return {'status': 'error', 'message': f'Client avec l email {user_email} n existe pas'}
            client = client_data[0]  # Obtenir le premier client de la liste

        logging.debug(f"Données du client : {client}")

        # Obtenir les données du vol par ID
        flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{flight_id}/'
        async with session.get(flight_url) as flight_response:
            if flight_response.status != 200:
                logging.error(f"Échec de la récupération des données du vol pour l'ID {flight_id}")
                return {'status': 'error', 'message': f'Vol avec l ID {flight_id} n existe pas'}
            flight = await flight_response.json()

        logging.debug(f"Données du vol : {flight}")

        # Vérifier si la réservation existe déjà
        reservation_check_url = f'http://127.0.0.1:8002/API-reservation/reservations/?client={client["id"]}&flight={flight["id"]}'
        async with session.get(reservation_check_url) as reservation_check_response:
            if reservation_check_response.status == 200:
                existing_reservations = await reservation_check_response.json()
                filtered_reservations = [res for res in existing_reservations if res['client'] == client['id'] and res['flight'] == flight['id']]
                logging.debug(f"Réservations filtrées pour le client {client['id']} et le vol {flight['id']} : {filtered_reservations}")
                if filtered_reservations:
                    return {'status': 'error', 'message': 'Vous avez déjà réservé ce vol.'}

        # Créer la réservation si des sièges sont disponibles
        if flight['sieges_disponible'] > 0:
            reservation_data = {
                'client': client['id'],
                'flight': flight['id'],
                'prix_ticket': flight['prix']
            }
            async with session.post('http://127.0.0.1:8002/API-reservation/reservations/', json=reservation_data) as reservation_response:
                if reservation_response.status == 201:
                    logging.debug("Réservation créée avec succès")
                    flight['sieges_disponible'] -= 1
                    async with session.put(flight_url, json=flight) as update_response:
                        if update_response.status == 200:
                            return {'status': 'success', 'message': 'Réservation réussie'}
                        else:
                            logging.error("Échec de la mise à jour de la disponibilité des sièges du vol")
                            return {'status': 'error', 'message': 'Échec de la mise à jour de la disponibilité des sièges du vol'}
                else:
                    logging.error("Échec de la création de la réservation")
                    return {'status': 'error', 'message': 'Échec de la création de la réservation'}
        else:
            return {'status': 'error', 'message': 'Aucun siège disponible'}

async def get_user_reservations(user_email):
    """
    Obtient les réservations pour un utilisateur donné par son email.

    Args:
        user_email (str): L'email de l'utilisateur.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des réservations.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données du client par email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Échec de la récupération des données du client pour l'email {user_email}")
                return {'status': 'error', 'message': f'Client avec l email {user_email} n existe pas'}
            client_data = await client_response.json()
            if not client_data:
                return {'status': 'error', 'message': f'Client avec l email {user_email} n existe pas'}
            client = client_data[0]  # Obtenir le premier client de la liste

        logging.debug(f"Données du client : {client}")

        # Obtenir les réservations par ID de client
        reservations_url = f'http://127.0.0.1:8002/API-reservation/reservations/?client={client["id"]}'
        async with session.get(reservations_url) as reservations_response:
            if reservations_response.status == 200:
                reservations = await reservations_response.json()
                client_reservations = []
                for res in reservations:
                    if res['client'] == client['id']:
                        res['prix_ticket'] = str(res['prix_ticket'])  # Convertir Decimal en chaîne
                        # Obtenir les détails du vol
                        flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                        async with session.get(flight_url) as flight_response:
                            if flight_response.status == 200:
                                flight = await flight_response.json()
                                res['flight_details'] = flight
                        client_reservations.append(res)
                logging.debug(f"Réservations pour le client {client['id']} : {client_reservations}")
                return {'status': 'success', 'data': client_reservations}
            else:
                logging.error("Échec de la récupération des réservations")
                return {'status': 'error', 'message': 'Échec de la récupération des réservations'}

async def cancel_reservation(reservation_id):
    """
    Annule une réservation par son ID.

    Args:
        reservation_id (int): L'ID de la réservation.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données de la réservation
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Échec de la récupération des données de la réservation pour l'ID {reservation_id}")
                return {'status': 'error', 'message': f'Réservation avec l ID {reservation_id} n existe pas'}
            reservation = await reservation_response.json()

        logging.debug(f"Données de la réservation : {reservation}")

        # Supprimer la réservation
        async with session.delete(reservation_url) as delete_response:
            if delete_response.status == 204:
                logging.debug(f"Réservation {reservation_id} supprimée avec succès")

                # Mettre à jour la disponibilité des sièges du vol
                flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{reservation["flight"]}/'
                async with session.get(flight_url) as flight_response:
                    if flight_response.status == 200:
                        flight = await flight_response.json()
                        flight['sieges_disponible'] += 1
                        async with session.put(flight_url, json=flight) as update_response:
                            if update_response.status == 200:
                                logging.debug(f"Disponibilité des sièges mise à jour avec succès pour le vol {reservation['flight']}")
                                return {'status': 'success', 'message': 'Réservation annulée avec succès'}
                            else:
                                logging.error(f"Échec de la mise à jour de la disponibilité des sièges pour le vol {reservation['flight']}")
                                return {'status': 'error', 'message': 'Échec de la mise à jour de la disponibilité des sièges'}
                    else:
                        logging.error(f"Échec de la récupération des données du vol pour l'ID {reservation['flight']}")
                        return {'status': 'error', 'message': f'Échec de la récupération des données du vol pour l ID {reservation["flight"]}'}
            else:
                logging.error(f"Échec de la suppression de la réservation {reservation_id}")
                return {'status': 'error', 'message': 'Échec de l annulation de la réservation'}

async def get_all_reservations():
    """
    Récupère toutes les réservations et leurs détails associés.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des réservations.
    """
    async with aiohttp.ClientSession() as session:
        reservations_url = 'http://127.0.0.1:8002/API-reservation/reservations/'
        async with session.get(reservations_url) as reservations_response:
            if reservations_response.status == 200:
                reservations = await reservations_response.json()
                for res in reservations:
                    res['prix_ticket'] = str(res['prix_ticket'])  # Convertir Decimal en chaîne
                    # Obtenir les détails du client
                    client_url = f'http://127.0.0.1:8002/API-client/clients/{res["client"]}/'
                    async with session.get(client_url) as client_response:
                        if client_response.status == 200:
                            client = await client_response.json()
                            res['client_email'] = client['email']  # Ajouter l'email du client
                            logging.debug(f"Email du client pour la réservation {res['id']} : {res['client_email']}")
                        else:
                            logging.error(f"Échec de la récupération des données du client pour la réservation {res['id']}")
                            res['client_email'] = 'N/A'
                    # Obtenir les détails du vol
                    flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                    async with session.get(flight_url) as flight_response:
                        if flight_response.status == 200:
                            flight = await flight_response.json()
                            res['flight_details'] = flight
                logging.debug(f"Toutes les réservations récupérées : {reservations}")
                return {'status': 'success', 'data': reservations}
            else:
                logging.error("Échec de la récupération des réservations")
                return {'status': 'error', 'message': 'Échec de la récupération des réservations'}

async def validate_reservation(reservation_id):
    """
    Valide une réservation par son ID.

    Args:
        reservation_id (int): L'ID de la réservation.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données de la réservation
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Échec de la récupération des données de la réservation pour l'ID {reservation_id}")
                return {'status': 'error', 'message': f'Réservation avec l ID {reservation_id} n existe pas'}
            reservation = await reservation_response.json()

        # Mettre à jour le statut de validation de la réservation
        reservation['is_validated'] = True
        async with session.put(reservation_url, json=reservation) as update_response:
            if update_response.status == 200:
                logging.debug(f"Réservation {reservation_id} validée avec succès")
                return {'status': 'success', 'message': 'Réservation validée avec succès'}
            else:
                logging.error(f"Échec de la validation de la réservation {reservation_id}")
                return {'status': 'error', 'message': 'Échec de la validation de la réservation'}

async def revert_validate_reservation(reservation_id):
    """
    Annule la validation d'une réservation par son ID.

    Args:
        reservation_id (int): L'ID de la réservation.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données de la réservation
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Échec de la récupération des données de la réservation pour l'ID {reservation_id}")
                return {'status': 'error', 'message': f'Réservation avec l ID {reservation_id} n existe pas'}
            reservation = await reservation_response.json()

        # Mettre à jour le statut de validation de la réservation
        reservation['is_validated'] = False
        async with session.put(reservation_url, json=reservation) as update_response:
            if update_response.status == 200:
                logging.debug(f"Validation de la réservation {reservation_id} annulée avec succès")
                return {'status': 'success', 'message': 'Validation de la réservation annulée avec succès'}
            else:
                logging.error(f"Échec de l'annulation de la validation pour la réservation {reservation_id}")
                return {'status': 'error', 'message': 'Échec de l annulation de la validation de la réservation'}

async def run_reservations():
    """
    Exécute les opérations de réservation via NATS.
    """
    nc = NATS()

    # Connecter au serveur NATS
    try:
        await nc.connect(servers=["nats://localhost:4222"])
        logging.info("Connecté au serveur NATS")
    except Exception as e:
        logging.error(f"Échec de la connexion au serveur NATS : {e}")
        return

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()

        # Log des données reçues
        logging.debug(f"Message reçu sur le sujet '{subject}' : {data}")

        if not data:
            logging.error("Message reçu vide")
            if reply:
                await nc.publish(reply, json.dumps({'status': 'error', 'message': 'Message reçu vide'}).encode())
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON : {e}")
            if reply:
                await nc.publish(reply, json.dumps({'status': 'error', 'message': f'Erreur de décodage JSON : {e}'}).encode())
            return

        logging.debug(f"Requête reçue avec les données : {data}")

        if subject == "reserve_flight":
            response = await create_reservation(data.get('user_email'), data.get('flight_id'))
        elif subject == "get_reservations":
            response = await get_user_reservations(data.get('user_email'))
        elif subject == "cancel_reservation":
            response = await cancel_reservation(data.get('reservation_id'))
        elif subject == "get_all_reservations":
            response = await get_all_reservations()
        elif subject == "validate_reservation":
            response = await validate_reservation(data.get('reservation_id'))
        elif subject == "revert_validate_reservation":
            response = await revert_validate_reservation(data.get('reservation_id'))
        else:
            response = {'status': 'error', 'message': 'Sujet inconnu'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Réponse publiée : {response}")

    # S'abonner aux sujets pertinents
    subjects = ["reserve_flight", "get_reservations", "cancel_reservation", "get_all_reservations", "validate_reservation", "revert_validate_reservation"]
    for subject in subjects:
        try:
            await nc.subscribe(subject, cb=message_handler)
            logging.info(f"Abonné au sujet '{subject}'")
        except Exception as e:
            logging.error(f"Échec de l'abonnement au sujet '{subject}' : {e}")

    # Garder la connexion active
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interruption par l'utilisateur, fermeture de la connexion")
    finally:
        await nc.close()
        logging.info("Connexion NATS fermée")

if __name__ == "__main__":
    asyncio.run(run_reservations())