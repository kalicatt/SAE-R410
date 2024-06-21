from django.shortcuts import render, redirect, Http404
from django.http import JsonResponse
import json
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import logging
from django.views import View
from asgiref.sync import sync_to_async
from nats.aio.client import Client as NATS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def index(request):
    return render(request, 'index.html')


def destinations(request):
    return render(request, 'destinations.html')

@ensure_csrf_cookie
def signup_view(request):
    if request.method == 'POST':
        # Les données seront interceptées et envoyées à NATS par le middleware
        return redirect('signup_success')
    return render(request, 'signup.html')

def signup_success(request):
    return render(request, 'signup_success.html')

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.session['user'] = {'email': email, 'prenom': user.first_name, 'nom': user.last_name}
            logging.debug(f"User {email} logged in successfully.")
            return JsonResponse({'status': 'success'})
        else:
            logging.debug(f"Invalid login attempt for user {email}.")
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    return render(request, 'login.html')

@login_required
def login_success(request):
    return render(request, 'login_success.html')

def profile_view(request):
    user = request.session.get('user')
    logging.debug(f"Accessing profile for user {user}")
    return render(request, 'profile.html', {'user': user})

def flight_detail(request, flight_id, flight_type):
    if flight_type == 'departure':
        url = f'http://127.0.0.1:8002/API-depart/vol-depart/{flight_id}/'
    elif flight_type == 'arrival':
        url = f'http://127.0.0.1:8002/API-arriver/vol-arriver/{flight_id}/'
    else:
        raise Http404("Flight type is not valid")

    response = requests.get(url)
    if response.status_code == 200:
        flight = response.json()
        return render(request, 'flight_detail.html', {'flight': flight, 'flight_type': flight_type})
    else:
        raise Http404("Flight does not exist")
    
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')