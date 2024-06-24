import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_departures():
    """
    Récupère les départs depuis l'API.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des départs.
    """
    logging.debug("Récupération des départs depuis l'API...")
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8002/API-depart/vol-depart/') as response:
            if response.status == 200:
                departures = await response.json()
                for departure in departures:
                    departure['prix'] = str(departure['prix'])
                logging.debug(f"Départs récupérés : {departures}")
                return {'status': 'success', 'data': departures}
            else:
                logging.error(f"Échec de la récupération des départs, code de statut : {response.status}")
                return {'status': 'error', 'message': 'Échec de la récupération des départs'}

async def run_departures():
    """
    Exécute la récupération des départs via NATS.
    """
    logging.debug("Connexion au serveur NATS...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connecté au serveur NATS. Abonnement à 'get_departures'...")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        logging.debug(f"Message reçu sur le sujet '{subject}' avec réponse '{reply}'")

        if subject == "get_departures":
            response = await fetch_departures()
            if reply:
                await nc.publish(reply, json.dumps(response).encode())
                logging.debug(f"Réponse publiée : {response}")

    await nc.subscribe("get_departures", cb=message_handler)
    logging.debug("Abonné au sujet 'get_departures'")

if __name__ == "__main__":
    asyncio.run(run_departures())
