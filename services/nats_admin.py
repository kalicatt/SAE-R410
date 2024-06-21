import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_admin_status(user_email):
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

async def run_check_admin():
    nc = NATS()

    # Try connecting to the NATS server
    try:
        await nc.connect(servers=["nats://localhost:4222"])
        logging.info("Connected to NATS server")
    except Exception as e:
        logging.error(f"Failed to connect to NATS server: {e}")
        return

    async def message_handler(msg):
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
        else:
            response = {'status': 'error', 'message': 'Unknown subject'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Published response: {response}")

    # Subscribe to the 'check_admin' subject
    try:
        await nc.subscribe("check_admin", cb=message_handler)
        logging.info("Subscribed to 'check_admin' subject")
    except Exception as e:
        logging.error(f"Failed to subscribe to 'check_admin': {e}")

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
