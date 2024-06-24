import json
import aiohttp
import logging
from nats.aio.client import Client as NATS
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_client_by_id(client_id):
    logging.debug(f"Getting client by ID: {client_id}")
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8002/API-client/clients/{client_id}/'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                logging.debug(f"Client data for ID {client_id}: {data}")
                return data
            logging.error(f"Failed to get client for ID {client_id}, status code: {response.status}")
            return None

async def create_reservation(user_email, flight_id):
    async with aiohttp.ClientSession() as session:
        # Get client data by email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Failed to fetch client data for email {user_email}")
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client_data = await client_response.json()
            if not client_data:
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client = client_data[0]  # Get the first client in the list

        logging.debug(f"Client data: {client}")

        # Get flight data by id
        flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{flight_id}/'
        async with session.get(flight_url) as flight_response:
            if flight_response.status != 200:
                logging.error(f"Failed to fetch flight data for id {flight_id}")
                return {'status': 'error', 'message': f'Flight with id {flight_id} does not exist'}
            flight = await flight_response.json()

        logging.debug(f"Flight data: {flight}")

        # Check if reservation already exists
        reservation_check_url = f'http://127.0.0.1:8002/API-reservation/reservations/?client={client["id"]}&flight={flight["id"]}'
        async with session.get(reservation_check_url) as reservation_check_response:
            if reservation_check_response.status == 200:
                existing_reservations = await reservation_check_response.json()
                filtered_reservations = [res for res in existing_reservations if res['client'] == client['id'] and res['flight'] == flight['id']]
                logging.debug(f"Filtered reservations for client {client['id']} and flight {flight['id']}: {filtered_reservations}")
                if filtered_reservations:
                    return {'status': 'error', 'message': 'You have already reserved this flight.'}

        # Create reservation if seats are available
        if flight['sieges_disponible'] > 0:
            reservation_data = {
                'client': client['id'],
                'flight': flight['id'],
                'prix_ticket': flight['prix']
            }
            async with session.post('http://127.0.0.1:8002/API-reservation/reservations/', json=reservation_data) as reservation_response:
                if reservation_response.status == 201:
                    logging.debug("Reservation created successfully")
                    flight['sieges_disponible'] -= 1
                    async with session.put(flight_url, json=flight) as update_response:
                        if update_response.status == 200:
                            return {'status': 'success', 'message': 'Reservation successful'}
                        else:
                            logging.error("Failed to update flight seat availability")
                            return {'status': 'error', 'message': 'Failed to update flight seat availability'}
                else:
                    logging.error("Failed to create reservation")
                    return {'status': 'error', 'message': 'Failed to create reservation'}
        else:
            return {'status': 'error', 'message': 'No available seats'}

async def get_user_reservations(user_email):
    async with aiohttp.ClientSession() as session:
        # Get client data by email
        client_url = f'http://127.0.0.1:8002/API-client/clients/?email={user_email}'
        async with session.get(client_url) as client_response:
            if client_response.status != 200:
                logging.error(f"Failed to fetch client data for email {user_email}")
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client_data = await client_response.json()
            if not client_data:
                return {'status': 'error', 'message': f'Client with email {user_email} does not exist'}
            client = client_data[0]  # Get the first client in the list

        logging.debug(f"Client data: {client}")

        # Get reservations by client id
        reservations_url = f'http://127.0.0.1:8002/API-reservation/reservations/?client={client["id"]}'
        async with session.get(reservations_url) as reservations_response:
            if reservations_response.status == 200:
                reservations = await reservations_response.json()
                client_reservations = []
                for res in reservations:
                    if res['client'] == client['id']:
                        res['prix_ticket'] = str(res['prix_ticket'])  # Convert Decimal to string
                        # Get flight details
                        flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                        async with session.get(flight_url) as flight_response:
                            if flight_response.status == 200:
                                flight = await flight_response.json()
                                res['flight_details'] = flight
                        client_reservations.append(res)
                logging.debug(f"Reservations for client {client['id']}: {client_reservations}")
                return {'status': 'success', 'data': client_reservations}
            else:
                logging.error("Failed to fetch reservations")
                return {'status': 'error', 'message': 'Failed to fetch reservations'}

async def cancel_reservation(reservation_id):
    async with aiohttp.ClientSession() as session:
        # Get reservation data
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Failed to fetch reservation data for id {reservation_id}")
                return {'status': 'error', 'message': f'Reservation with id {reservation_id} does not exist'}
            reservation = await reservation_response.json()

        logging.debug(f"Reservation data: {reservation}")

        # Delete reservation
        async with session.delete(reservation_url) as delete_response:
            if delete_response.status == 204:
                logging.debug(f"Reservation {reservation_id} deleted successfully")

                # Update flight seat availability
                flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{reservation["flight"]}/'
                async with session.get(flight_url) as flight_response:
                    if flight_response.status == 200:
                        flight = await flight_response.json()
                        flight['sieges_disponible'] += 1
                        async with session.put(flight_url, json=flight) as update_response:
                            if update_response.status == 200:
                                logging.debug(f"Flight seat availability updated successfully for flight {reservation['flight']}")
                                return {'status': 'success', 'message': 'Reservation cancelled successfully'}
                            else:
                                logging.error(f"Failed to update flight seat availability for flight {reservation['flight']}")
                                return {'status': 'error', 'message': 'Failed to update flight seat availability'}
                    else:
                        logging.error(f"Failed to fetch flight data for id {reservation['flight']}")
                        return {'status': 'error', 'message': f'Failed to fetch flight data for id {reservation["flight"]}'}
            else:
                logging.error(f"Failed to delete reservation {reservation_id}")
                return {'status': 'error', 'message': 'Failed to cancel reservation'}

async def get_all_reservations():
    async with aiohttp.ClientSession() as session:
        reservations_url = 'http://127.0.0.1:8002/API-reservation/reservations/'
        async with session.get(reservations_url) as reservations_response:
            if reservations_response.status == 200:
                reservations = await reservations_response.json()
                for res in reservations:
                    res['prix_ticket'] = str(res['prix_ticket'])  # Convert Decimal to string
                    # Get client details
                    client_url = f'http://127.0.0.1:8002/API-client/clients/{res["client"]}/'
                    async with session.get(client_url) as client_response:
                        if client_response.status == 200:
                            client = await client_response.json()
                            res['client_email'] = client['email']  # Add client email
                            logging.debug(f"Client email for reservation {res['id']}: {res['client_email']}")
                        else:
                            logging.error(f"Failed to fetch client data for reservation {res['id']}")
                            res['client_email'] = 'N/A'
                    # Get flight details
                    flight_url = f'http://127.0.0.1:8002/API-depart/vol-depart/{res["flight"]}/'
                    async with session.get(flight_url) as flight_response:
                        if flight_response.status == 200:
                            flight = await flight_response.json()
                            res['flight_details'] = flight
                logging.debug(f"Fetched all reservations: {reservations}")
                return {'status': 'success', 'data': reservations}
            else:
                logging.error("Failed to fetch reservations")
                return {'status': 'error', 'message': 'Failed to fetch reservations'}

async def validate_reservation(reservation_id):
    async with aiohttp.ClientSession() as session:
        # Get reservation data
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Failed to fetch reservation data for id {reservation_id}")
                return {'status': 'error', 'message': f'Reservation with id {reservation_id} does not exist'}
            reservation = await reservation_response.json()

        # Update reservation validation status
        reservation['is_validated'] = True
        async with session.put(reservation_url, json=reservation) as update_response:
            if update_response.status == 200:
                logging.debug(f"Reservation {reservation_id} validated successfully")
                return {'status': 'success', 'message': 'Reservation validated successfully'}
            else:
                logging.error(f"Failed to validate reservation {reservation_id}")
                return {'status': 'error', 'message': 'Failed to validate reservation'}

async def revert_validate_reservation(reservation_id):
    async with aiohttp.ClientSession() as session:
        # Get reservation data
        reservation_url = f'http://127.0.0.1:8002/API-reservation/reservations/{reservation_id}/'
        async with session.get(reservation_url) as reservation_response:
            if reservation_response.status != 200:
                logging.error(f"Failed to fetch reservation data for id {reservation_id}")
                return {'status': 'error', 'message': f'Reservation with id {reservation_id} does not exist'}
            reservation = await reservation_response.json()

        # Update reservation validation status
        reservation['is_validated'] = False
        async with session.put(reservation_url, json=reservation) as update_response:
            if update_response.status == 200:
                logging.debug(f"Reservation {reservation_id} validation reverted successfully")
                return {'status': 'success', 'message': 'Reservation validation reverted successfully'}
            else:
                logging.error(f"Failed to revert validation for reservation {reservation_id}")
                return {'status': 'error', 'message': 'Failed to revert reservation validation'}

async def run_reservations():
    nc = NATS()

    # Connect to the NATS server
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

        # Log received data
        logging.debug(f"Received message on subject '{subject}': {data}")

        if not data:
            logging.error("Received empty message")
            if reply:
                await nc.publish(reply, json.dumps({'status': 'error', 'message': 'Received empty message'}).encode())
            return

        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            if reply:
                await nc.publish(reply, json.dumps({'status': 'error', 'message': f'JSON decode error: {e}'}).encode())
            return

        logging.debug(f"Received request with data: {data}")

        if subject == "reserve_flight":
            response = await create_reservation(data.get('user_email'), data.get('flight_id'))
        elif subject == "get_reservations":
            response = await get_user_reservations(data.get('user_email'))
        elif subject == "cancel_reservation":
            response = await cancel_reservation(data.get('reservation_id'))
        elif subject == "get_all_reservations":
            response = await get_all_reservations()
        elif subject == "validate_reservation":
            response = await validate_reservation(data.get('reservation_id'))
        elif subject == "revert_validate_reservation":
            response = await revert_validate_reservation(data.get('reservation_id'))
        else:
            response = {'status': 'error', 'message': 'Unknown subject'}

        if reply:
            await nc.publish(reply, json.dumps(response).encode())
            logging.debug(f"Published response: {response}")

    # Subscribe to the relevant subjects
    subjects = ["reserve_flight", "get_reservations", "cancel_reservation", "get_all_reservations", "validate_reservation", "revert_validate_reservation"]
    for subject in subjects:
        try:
            await nc.subscribe(subject, cb=message_handler)
            logging.info(f"Subscribed to subject '{subject}'")
        except Exception as e:
            logging.error(f"Failed to subscribe to subject '{subject}': {e}")

    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt, closing connection")
    finally:
        await nc.close()
        logging.info("NATS connection closed")

if __name__ == "__main__":
    asyncio.run(run_reservations())
