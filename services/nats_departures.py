import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio
from datetime import datetime

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def format_date(date_str):
    """
    Formatte une date au format 'jour/mois/année heure:minute'.

    Args:
        date_str (str): La date en chaîne de caractères.

    Returns:
        str: La date formatée.

    Exemple:
        date_formattee = format_date("2023-06-25T14:00:00Z")
        print(date_formattee)  # Output: '25/06/2023 14:00'
    """
    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return date.strftime('%d/%m/%Y %H:%M')

async def fetch_departures():
    """
    Récupère les départs depuis l'API.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et les données des départs.

    Exemple:
        departures = await fetch_departures()
        print(departures)
    """
    logging.debug("Récupération des départs depuis l'API...")
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8002/API-depart/vol-depart/') as response:
            if response.status == 200:
                departures = await response.json()
                for departure in departures:
                    departure['prix'] = str(departure['prix'])
                    departure['formatted_departure_time'] = format_date(departure['departure_time'])
                logging.debug(f"Départs récupérés : {departures}")
                return {'status': 'success', 'data': departures}
            else:
                logging.error(f"Échec de la récupération des départs, code de statut : {response.status}")
                return {'status': 'error', 'message': 'Échec de la récupération des départs'}

async def run_departures():
    """
    Exécute la récupération des départs via NATS.

    Exemple:
        asyncio.run(run_departures())
    """
    logging.debug("Connexion au serveur NATS...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connecté au serveur NATS. Abonnement à 'get_departures'...")

    async def message_handler(msg):
        """
        Gère les messages reçus sur le sujet 'get_departures'.

        Args:
            msg: Le message reçu de NATS.

        Returns:
            None
        """
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
