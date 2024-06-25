import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_client_exists(email):
    """
    Vérifie si un client existe pour un email donné.

    Args:
        email (str): L'email du client à vérifier.

    Returns:
        bool: True si le client existe, False sinon.
    """
    logging.debug(f"Vérification de l'existence du client pour l'email : {email}")
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/?email={email}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Réponse de l'API pour l'email {email} : {data}")
                if isinstance(data, list) and len(data) > 0:
                    return True
                return False
            logging.error(f"Échec de la vérification de l'existence du client pour l'email {email}, code de statut : {response.status}")
            return False

async def save_client_data(data):
    """
    Enregistre les données d'un client.

    Args:
        data (dict): Les données du client à enregistrer.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    logging.debug(f"Enregistrement des données du client : {data}")
    if await check_client_exists(data['email']):
        logging.debug(f"Le client avec l'email {data['email']} existe déjà")
        return {'status': 'error', 'message': 'Email already exists'}

    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8002/API-client/clients/', json=data) as response:
            if response.status == 201:
                logging.debug("Client enregistré avec succès")
                return {'status': 'success'}
            else:
                error_data = await response.json()
                logging.debug(f"Erreur lors de l'enregistrement du client : {error_data}")
                return {'status': 'error', 'message': error_data}

async def async_authenticate(email, password):
    """
    Authentifie un utilisateur.

    Args:
        email (str): L'email de l'utilisateur.
        password (str): Le mot de passe de l'utilisateur.

    Returns:
        bool: True si l'authentification réussit, False sinon.
    """
    logging.debug(f"Authentification de l'utilisateur avec l'email : {email}")
    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8002/API-client/authenticate/', json={'email': email, 'password': password}) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Réponse d'authentification pour {email} : {data}")
                return data.get('authenticated', False)
    return False

async def get_client_by_email(email):
    """
    Obtient les informations d'un client par son email.

    Args:
        email (str): L'email du client.

    Returns:
        dict: Les données du client si elles existent, None sinon.
    """
    logging.debug(f"Obtention du client par email : {email}")
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/?email={email}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Données du client pour {email} : {data}")
                if isinstance(data, list) and len(data) > 0:
                    return data[0]  # Supposons que l'API renvoie une liste de clients
            logging.error(f"Échec de l'obtention du client pour l'email {email}, code de statut : {response.status}")
            return None

async def authenticate_user(data):
    """
    Authentifie un utilisateur avec ses données.

    Args:
        data (dict): Les données de l'utilisateur pour l'authentification.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les informations de l'utilisateur si l'authentification réussit.
    """
    logging.debug(f"Authentification de l'utilisateur avec les données : {data}")
    authenticated = await async_authenticate(data['email'], data['password'])
    if authenticated:
        client = await get_client_by_email(data['email'])
        if client:
            return {'status': 'success', 'nom': client['nom'], 'prenom': client['prenom']}
    return {'status': 'error', 'message': 'Invalid credentials'}

async def verify_email(email):
    """
    Vérifie si un email est unique.

    Args:
        email (str): L'email à vérifier.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et l'information de l'unicité de l'email.
    """
    logging.debug(f"Vérification de l'unicité de l'email : {email}")
    exists = await check_client_exists(email)
    return {'status': 'success', 'is_unique': not exists}

async def get_client_money_by_email(email):
    """
    Récupère l'argent du client par email.

    Args:
        email (str): L'email du client.

    Returns:
        dict: Un dictionnaire contenant l'argent du client.
    """
    logging.debug(f"Obtention de l'argent du client pour l'email : {email}")
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/?email={email}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Réponse de l'API pour l'email {email} : {data}")
                if isinstance(data, list) and len(data) > 0:
                    client = data[0]
                    return {'status': 'success', 'argent': client['argent']}
                return {'status': 'error', 'message': 'Client not found'}
            logging.error(f"Échec de l'obtention du client pour l'email {email}, code de statut : {response.status}")
            return {'status': 'error', 'message': 'Failed to fetch client data'}

async def run_login_signup():
    """
    Exécute le processus de connexion, d'inscription et de vérification d'email via NATS.

    Exemple:
        asyncio.run(run_login_signup())
    """
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    async def message_handler(msg):
        """
        Gère les messages reçus sur les sujets 'signup', 'login', 'verify_email', et 'get_client_money'.

        Args:
            msg: Le message reçu de NATS.

        Returns:
            None
        """
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data) if data else {}
        logging.debug(f"Message reçu sur le sujet {subject} : {data}")
        if subject == "signup":
            response = await save_client_data(data)
        elif subject == "login":
            response = await authenticate_user(data)
        elif subject == "verify_email":
            response = await verify_email(data.get('email'))
        elif subject == "get_client_money":
            response = await get_client_money_by_email(data.get('email'))
        else:
            response = {'status': 'error', 'message': 'Sujet inconnu'}
        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Réponse publiée : {response}")

    await nc.subscribe("signup", cb=message_handler)
    await nc.subscribe("login", cb=message_handler)
    await nc.subscribe("verify_email", cb=message_handler)
    await nc.subscribe("get_client_money", cb=message_handler)
    logging.debug("Abonné aux sujets 'signup', 'login', 'verify_email', et 'get_client_money'")

if __name__ == "__main__":
    asyncio.run(run_login_signup())