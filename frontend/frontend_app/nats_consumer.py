import asyncio
import json
from nats.aio.client import Client as NATS
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aeroport_project.settings')
import django
django.setup()

async def start_nats_consumer():
    nc = NATS()

    await nc.connect(servers=["nats://localhost:4222"])  # Assurez-vous que cette adresse est correcte

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"Received a message on '{subject}': {data}")

        # Traiter les données de l'inscription
        data = json.loads(data)
        print("Processed data:", data)

        # Simuler une réponse
        response = {'status': 'success'}
        
        # Répondre uniquement s'il y a une adresse de réponse
        if msg.reply:
            await nc.publish(msg.reply, json.dumps(response).encode())

    await nc.subscribe("signup", cb=message_handler)

    print("NATS consumer started and listening for messages...")
    await asyncio.Event().wait()

# Commande pour exécuter le consommateur
if __name__ == "__main__":
    asyncio.run(start_nats_consumer())
