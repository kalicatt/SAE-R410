import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def change_password(data):
    """
    Change le mot de passe du client.

    Args:
        data (dict): Les données contenant l'email du client et le nouveau mot de passe.

    Returns:
        dict: Un dictionnaire contenant le statut de l'opération et un message.
    """
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return {'status': 'error', 'message': 'Email and new password are required'}

    logging.debug(f"Changement de mot de passe pour l'email : {email}")

    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/change_password/'
        payload = {
            'email': email,
            'new_password': new_password
        }
        async with session.put(url, json=payload) as response:
            if response.status == 200:
                logging.debug("Mot de passe changé avec succès")
                return {'status': 'success', 'message': 'Password changed successfully'}
            else:
                error_data = await response.json()
                logging.error(f"Erreur lors du changement de mot de passe : {error_data}")
                return {'status': 'error', 'message': error_data.get('detail', 'Failed to change password')}

async def run_password_service():
    """
    Exécute le service de changement de mot de passe via NATS.
    """
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        data = json.loads(data) if data else {}
        logging.debug(f"Message reçu sur le sujet {subject} : {data}")

        if subject == "change_password":
            response = await change_password(data)
        else:
            response = {'status': 'error', 'message': 'Unknown subject'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Réponse publiée : {response}")

    await nc.subscribe("change_password", cb=message_handler)
    logging.debug("Abonné au sujet 'change_password'")

if __name__ == "__main__":
    asyncio.run(run_password_service())
