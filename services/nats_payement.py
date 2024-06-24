import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def process_payment(nc, payment_data):
    logging.debug("Processing payment with data: %s", payment_data)
    async with aiohttp.ClientSession() as session:
        # Simuler une demande de paiement à la banque
        banque_response = {
            'status': 'success',
            'transaction_id': 'txn_1234567890'
        }
        if banque_response['status'] == 'success':
            # Vérifier et mettre à jour le solde via nats_money
            response = await nc.request("check_and_update_balance", json.dumps(payment_data).encode())
            response_data = json.loads(response.data.decode())
            if response_data['status'] != 'success':
                logging.error(f"Failed to update client balance: {response_data['message']}")
                return {'status': 'error', 'message': response_data['message']}
            client_id = response_data['client_id']

            # Créer un enregistrement de paiement
            paiement_data = {
                'client': client_id,
                'reservation': payment_data['reservation_id'],
                'montant': payment_data['amount'],
                'client_email': payment_data['client_email'],
                'paiement_methode': payment_data['method'],
                'status': 'Completed'
            }
            async with session.post('http://127.0.0.1:8002/API-paiement/paiements/', json=paiement_data) as paiement_response:
                if paiement_response.status == 201:
                    logging.debug("Payment record created successfully")

                    # Mettre à jour le statut de la réservation
                    reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{payment_data["reservation_id"]}/'
                    async with session.get(reservation_url) as reservation_response:
                        if reservation_response.status == 200:
                            reservation_data = await reservation_response.json()
                            reservation_data['is_paid'] = True
                            async with session.put(reservation_url, json=reservation_data) as update_response:
                                if update_response.status == 200:
                                    logging.debug("Reservation status updated successfully")
                                    return {'status': 'success', 'message': 'Payment processed and reservation updated successfully'}
                                else:
                                    logging.error(f"Failed to update reservation status: {update_response.status}, {await update_response.text()}")
                                    return {'status': 'error', 'message': 'Failed to update reservation status'}
                        else:
                            logging.error(f"Failed to retrieve reservation: {reservation_response.status}, {await reservation_response.text()}")
                            return {'status': 'error', 'message': 'Failed to retrieve reservation'}
                else:
                    logging.error(f"Failed to create payment record: {paiement_response.status}, {await paiement_response.text()}")
                    return {'status': 'error', 'message': 'Failed to create payment record'}
        else:
            logging.error("Payment failed with bank")
            return {'status': 'error', 'message': 'Payment failed'}

async def run_payment():
    logging.debug("Connecting to NATS server...")
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])

    logging.debug("Connected to NATS server. Subscribing to 'process_payment'...")

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = json.loads(msg.data.decode())
        logging.debug(f"Received payment request with data: {data}")

        if subject == "process_payment":
            response = await process_payment(nc, data)
            if reply:
                await nc.publish(reply, json.dumps(response).encode())
                logging.debug(f"Published response: {response}")

    await nc.subscribe("process_payment", cb=message_handler)
    logging.debug("Subscribed to 'process_payment'")

if __name__ == "__main__":
    asyncio.run(run_payment())
