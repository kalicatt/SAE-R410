import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_and_update_balance(payment_data):
    async with aiohttp.ClientSession() as session:
        client_email = payment_data['client_email']
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={client_email}'
        
        async with session.get(client_url) as response:
            client_data = await response.json()
            if response.status != 200 or not client_data:
                logging.error(f"Failed to fetch client details: {response.status}, {client_data}")
                return {'status': 'error', 'message': 'Failed to fetch client details'}

            client = client_data[0]  # assuming email is unique and returns one client
            current_balance = float(client['argent'])  # Convert the balance to float

            if current_balance >= float(payment_data['amount']):
                new_balance = current_balance - float(payment_data['amount'])
                # Ensure the new balance does not exceed 10 digits in total
                new_balance = round(new_balance, 2)  # assuming 2 decimal places
                update_data = {'argent': new_balance}
                update_url = f'http://127.0.0.1:8002/API-client/clients/{client["id"]}/'
                async with session.put(update_url, json=update_data) as update_response:
                    if update_response.status == 200:
                        logging.debug("Client balance updated successfully")
                        return {'status': 'success', 'message': 'Client balance updated successfully', 'client_id': client['id']}
                    else:
                        logging.error(f"Failed to update client balance: {update_response.status}, {await update_response.text()}")
                        return {'status': 'error', 'message': 'Failed to update client balance'}
            else:
                logging.error("Insufficient balance")
                return {'status': 'error', 'message': 'Vous n avez pas assez d argent pour effectuer cette transaction'}

async def run_money():
    logging.debug("Connecting to NATS server...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connected to NATS server. Subscribing to 'check_and_update_balance'...")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        logging.debug(f"Received balance check request with data: {data}")

        if subject == "check_and_update_balance":
            response = await check_and_update_balance(data)
            if reply:
                await nc.publish(reply, json.dumps(response).encode())
                logging.debug(f"Published response: {response}")

    await nc.subscribe("check_and_update_balance", cb=message_handler)
    logging.debug("Subscribed to 'check_and_update_balance'")

if __name__ == "__main__":
    asyncio.run(run_money())
