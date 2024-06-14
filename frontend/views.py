from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def offers(request):
    return render(request, 'offers.html')

def seats(request):
    return render(request, 'seats.html')

def destinations(request):
    return render(request, 'destinations.html')

def login(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def signup_success(request):
    return render(request, 'signup_success.html')
