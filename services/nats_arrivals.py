import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_arrivals():
    """
    Récupère les arrivées depuis l'API des vols arrivés.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des arrivées.

    Exemple:
        arrivals = await fetch_arrivals()
        print(arrivals)
    """
    logging.debug("Fetching arrivals from API...")
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8002/API-arriver/vol-arriver/') as response:
            if response.status == 200:
                arrivals = await response.json()
                logging.debug(f"Fetched arrivals: {arrivals}")
                return {'status': 'success', 'data': arrivals}
            else:
                logging.error(f"Failed to fetch arrivals, status code: {response.status}")
                return {'status': 'error', 'message': 'Failed to fetch arrivals'}

async def run_arrivals():
    """
    Se connecte au serveur NATS, s'abonne au sujet 'get_arrivals', et gère les messages reçus sur ce sujet.

    Exemple:
        asyncio.run(run_arrivals())
    """
    logging.debug("Connecting to NATS server...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connected to NATS server. Subscribing to 'get_arrivals'...")

    async def message_handler(msg):
        """
        Gère les messages reçus sur le sujet 'get_arrivals'.

        Args:
            msg: Le message reçu de NATS.

        Returns:
            None
        """
        subject = msg.subject
        reply = msg.reply
        logging.debug(f"Received message on subject '{subject}' with reply '{reply}'")

        if subject == "get_arrivals":
            response = await fetch_arrivals()
            if reply:
                await nc.publish(reply, json.dumps(response).encode())
                logging.debug(f"Published response: {response}")

    await nc.subscribe("get_arrivals", cb=message_handler)
    logging.debug("Subscribed to 'get_arrivals'")

if __name__ == "__main__":
    asyncio.run(run_arrivals())
