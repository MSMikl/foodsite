import email
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from backend.models import Type, Allergy, User


class IndexView(TemplateView):
    template_name = "index.html"


class AuthView(TemplateView):
    template_name = "auth.html"


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "auth.html")

    def post(self, request):
        print(request.POST)
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        print(user)
        if user:
            login(request, user)
            return render(request, 'lk.html')

        return render(request, "auth.html")


class OrderView(View):
    def get(self, request):
        types = [{
            'id': type.id,
            'title': type.name,
            'price': type.price
        } for type in Type.objects.all()]
        print(types)
        allergies = [{
            'title': allergy.name,
            'id': allergy.id,
            } for allergy in Allergy.objects.all()]
        return render(request, 'order.html', context={
            'types': types,
            'allergies': allergies
        })

    def post(self, request):
        print(request.POST)
        print(request.user)
        return redirect('../')


class RegisterView(View):
    def get(self, request):
        return render(request, 'registration.html')

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        if not email or not name or not password:
            return render(request, 'registration.html', context={
                'error': 'Пожалуйста, введите имя, email и пароль',
            })
        user = User.objects.create_user(email=email, password=password, name=name)
        if user:
            login(request, user)
            return render(request, 'lk.html')
        print(user)
        return redirect('/')
