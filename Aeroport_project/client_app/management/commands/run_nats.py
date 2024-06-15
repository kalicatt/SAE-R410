# client_app/management/commands/run_nats.py
import asyncio
import json
from nats.aio.client import Client as NATS
from django.core.management.base import BaseCommand
from client_app.models import Clients
from django.contrib.auth import authenticate
from asgiref.sync import sync_to_async
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aeroport_project.settings')
import django
django.setup()

class Command(BaseCommand):
    help = 'Run NATS subscriber'

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
        loop.run_forever()

async def save_client_data(data):
    serializer = ClientSerializer(data=data)
    if serializer.is_valid():
        await sync_to_async(serializer.save)()
        return {'status': 'success'}
    else:
        return {'status': 'error', 'message': serializer.errors}

async def authenticate_user(data):
    user = await sync_to_async(authenticate)(username=data['email'], password=data['password'])
    if user is not None:
        return {'status': 'success'}
    else:
        return {'status': 'error', 'message': 'Invalid credentials'}

async def run():
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Received a message on '{subject}': {data}")

        # Process the data based on subject
        data = json.loads(data)
        if subject == "signup":
            response = await save_client_data(data)
        elif subject == "login":
            response = await authenticate_user(data)

        if reply:  # Check if reply subject is present and not empty
            await nc.publish(reply, json.dumps(response).encode())

    await nc.subscribe("signup", cb=message_handler)
    await nc.subscribe("login", cb=message_handler)

if __name__ == '__main__':
    asyncio.run(run())
