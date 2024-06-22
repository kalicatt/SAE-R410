import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_admin_status(user_email):
    """
    Vérifie si un utilisateur est administrateur en fonction de son email.
    
    Args:
        user_email (str): L'email de l'utilisateur à vérifier.
        
    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et si l'utilisateur est administrateur.
    """
    async with aiohttp.ClientSession() as session:
        # Obtenir les données du client par email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Échec de la récupération des données client pour l'email {user_email}, code de statut : {client_response.status}")
                return {'status': 'erreur', 'message': f'Client avec l email {user_email} n existe pas'}
            client_data = await client_response.json()
            if not client_data:
                logging.error(f"Aucune donnée client trouvée pour l'email {user_email}")
                return {'status': 'erreur', 'message': f'Client avec l email {user_email} n existe pas'}
            client = client_data[0]  # Obtenir le premier client de la liste
            logging.debug(f"Données du client : {client}")
            
            if client.get('is_staff') or client.get('is_superuser'):
                return {'status': 'succès', 'is_admin': True}
            else:
                return {'status': 'succès', 'is_admin': False}

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
                    # Obtenir les détails du vol
                    flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                    async with session.get(flight_url) as flight_response:
                        if flight_response.status == 200:
                            flight = await flight_response.json()
                            res['flight_details'] = flight
                logging.debug(f"Toutes les réservations récupérées : {reservations}")
                return {'status': 'succès', 'data': reservations}
            else:
                logging.error("Échec de la récupération des réservations")
                return {'status': 'erreur', 'message': 'Échec de la récupération des réservations'}

async def run_check_admin():
    """
    Exécute la vérification de l'administrateur et la récupération des réservations via NATS.
    """
    nc = NATS()

    # Essayer de se connecter au serveur NATS
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

        logging.debug(f"Message reçu sur le sujet '{subject}' : {data}")

        if not data:
            logging.error("Message reçu vide")
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON : {e}")
            return

        logging.debug(f"Requête de vérification d'admin reçue avec les données : {data}")

        if subject == "check_admin":
            response = await check_admin_status(data.get('user_email'))
        elif subject == "get_all_reservations":
            response = await get_all_reservations()
        else:
            response = {'status': 'erreur', 'message': 'Sujet inconnu'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Réponse publiée : {response}")

    # S'abonner aux sujets 'check_admin' et 'get_all_reservations'
    try:
        await nc.subscribe("check_admin", cb=message_handler)
        logging.info("Abonné au sujet 'check_admin'")
        await nc.subscribe("get_all_reservations", cb=message_handler)
        logging.info("Abonné au sujet 'get_all_reservations'")
    except Exception as e:
        logging.error(f"Échec de l'abonnement aux sujets : {e}")

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
    asyncio.run(run_check_admin())
