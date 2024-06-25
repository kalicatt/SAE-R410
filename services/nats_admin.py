import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_admin_status(user_email):
    """
    Vérifie si l'utilisateur avec l'email fourni a le statut administrateur.

    Args:
        user_email (str): L'email de l'utilisateur à vérifier.

    Returns:
        dict: Un dictionnaire contenant le statut de la vérification et une indication si l'utilisateur est administrateur.

    Exemple:
        result = await check_admin_status("exemple@domaine.com")
        print(result)
    """
    async with aiohttp.ClientSession() as session:
        # Get client data by email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Failed to fetch client data for email {user_email}, status code: {client_response.status}")
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client_data = await client_response.json()
            if not client_data:
                logging.error(f"No client data found for email {user_email}")
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client = client_data[0]  # Get the first client in the list
            logging.debug(f"Client data: {client}")
            
            if client.get('is_staff') or client.get('is_superuser'):
                return {'status': 'success', 'is_admin': True}
            else:
                return {'status': 'success', 'is_admin': False}

async def get_all_reservations():
    """
    Récupère toutes les réservations et ajoute les détails des vols à chaque réservation.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des réservations.

    Exemple:
        reservations = await get_all_reservations()
        print(reservations)
    """
    async with aiohttp.ClientSession() as session:
        reservations_url = 'http://127.0.0.1:8002/API-reservation/reservations/'
        async with session.get(reservations_url) as reservations_response:
            if reservations_response.status == 200:
                reservations = await reservations_response.json()
                for res in reservations:
                    res['prix_ticket'] = str(res['prix_ticket'])  # Convert Decimal to string
                    # Get flight details
                    flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                    async with session.get(flight_url) as flight_response:
                        if flight_response.status == 200:
                            flight = await flight_response.json()
                            res['flight_details'] = flight
                logging.debug(f"Fetched all reservations: {reservations}")
                return {'status': 'success', 'data': reservations}
            else:
                logging.error("Failed to fetch reservations")
                return {'status': 'error', 'message': 'Failed to fetch reservations'}

async def run_check_admin():
    """
    Se connecte au serveur NATS, s'abonne aux sujets 'check_admin' et 'get_all_reservations', 
    et gère les messages reçus sur ces sujets.

    Exemple:
        asyncio.run(run_check_admin())
    """
    nc = NATS()

    # Try connecting to the NATS server
    try:
        await nc.connect(servers=["nats://localhost:4222"])
        logging.info("Connected to NATS server")
    except Exception as e:
        logging.error(f"Failed to connect to NATS server: {e}")
        return

    async def message_handler(msg):
        """
        Gère les messages reçus sur les sujets 'check_admin' et 'get_all_reservations'.

        Args:
            msg: Le message reçu de NATS.

        Returns:
            None
        """
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()

        logging.debug(f"Received message on subject '{subject}': {data}")

        if not data:
            logging.error("Received empty message")
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return

        logging.debug(f"Received check admin request with data: {data}")

        if subject == "check_admin":
            response = await check_admin_status(data.get('user_email'))
        elif subject == "get_all_reservations":
            response = await get_all_reservations()
        else:
            response = {'status': 'error', 'message': 'Unknown subject'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Published response: {response}")

    # Subscribe to the 'check_admin' and 'get_all_reservations' subjects
    try:
        await nc.subscribe("check_admin", cb=message_handler)
        logging.info("Subscribed to 'check_admin' subject")
        await nc.subscribe("get_all_reservations", cb=message_handler)
        logging.info("Subscribed to 'get_all_reservations' subject")
    except Exception as e:
        logging.error(f"Failed to subscribe to subjects: {e}")

    # Keep the connection alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, closing connection")
    finally:
        await nc.close()
        logging.info("NATS connection closed")

if __name__ == "__main__":
    asyncio.run(run_check_admin())
