import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_arrivals():
    """
    Récupère les arrivées depuis l'API.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des arrivées.
    """
    logging.debug("Récupération des arrivées depuis l'API...")
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8002/API-arriver/vol-arriver/') as response:
            if response.status == 200:
                arrivals = await response.json()
                logging.debug(f"Arrivées récupérées : {arrivals}")
                return {'status': 'succès', 'data': arrivals}
            else:
                logging.error(f"Échec de la récupération des arrivées, code de statut : {response.status}")
                return {'status': 'erreur', 'message': 'Échec de la récupération des arrivées'}

async def run_arrivals():
    """
    Exécute la récupération des arrivées via NATS.
    """
    logging.debug("Connexion au serveur NATS...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connecté au serveur NATS. Abonnement à 'get_arrivals'...")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        logging.debug(f"Message reçu sur le sujet '{subject}' avec réponse '{reply}'")

        if subject == "get_arrivals":
            response = await fetch_arrivals()
            if reply:
                await nc.publish(reply, json.dumps(response).encode())
                logging.debug(f"Réponse publiée : {response}")

    await nc.subscribe("get_arrivals", cb=message_handler)
    logging.debug("Abonné à 'get_arrivals'")

if __name__ == "__main__":
    asyncio.run(run_arrivals())
