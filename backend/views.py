from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


class AuthView(TemplateView):
    template_name = "auth.html"


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "auth.html")

    def post(self, request):
        print(request.POST)
        username = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return render(request, 'lk.html')

        return render(request, "auth.html")
