# frontend_app/middleware.py
import json
import asyncio
from django.utils.deprecation import MiddlewareMixin
from nats.aio.client import Client as NATS
from django.contrib.auth import authenticate, login as auth_login

class NatsMiddleware(MiddlewareMixin):

    async def send_to_nats(self, subject, data):
        nc = NATS()
        await nc.connect(servers=["nats://localhost:4222"])
        print(f"Sending data to NATS on subject '{subject}': {data}")
        await nc.publish(subject, json.dumps(data).encode())
        await nc.flush()
        await nc.close()

    def process_request(self, request):
        if request.method == 'POST':
            if request.path == '/signup/' and not getattr(request, '_nats_processed', False):
                data = {
                    'nom': request.POST.get('nom'),
                    'prenom': request.POST.get('prenom'),
                    'email': request.POST.get('email'),
                    'mot_de_passe': request.POST.get('mot_de_passe'),
                    'telephone': request.POST.get('telephone'),
                    'adresse': request.POST.get('adresse'),
                    'ville': request.POST.get('ville'),
                    'code_postal': request.POST.get('code_postal'),
                    'pays': request.POST.get('pays'),
                    'date_naissance': request.POST.get('date_naissance'),
                }
                print(f"Received data in middleware: {data}")
                asyncio.run(self.send_to_nats("signup", data))
                request._nats_processed = True

            if request.path == '/login/' and not getattr(request, '_nats_processed', False):
                try:
                    data = json.loads(request.body)
                    email = data.get('email')
                    password = data.get('password')
                except json.JSONDecodeError:
                    email = request.POST.get('email')
                    password = request.POST.get('password')

                user = authenticate(request, username=email, password=password)
                if user is not None:
                    auth_login(request, user)
                    data = {
                        'email': email,
                        'password': password
                    }
                    print(f"Received login data in middleware: {data}")
                    asyncio.run(self.send_to_nats("login", data))
                    request._nats_processed = True

        return None
