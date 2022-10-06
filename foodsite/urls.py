"""foodsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from backend.views import (
    IndexView, AuthView, LoginView, OrderView,
    RegisterView, RecipeView, CabinetView
)


urlpatterns = [
    path('', IndexView.as_view()),
    path('admin/', admin.site.urls),
    path('auth/', AuthView.as_view(), name='auth'),
    path('login/', LoginView.as_view(), name='login'),
    path('order/', OrderView.as_view(), name='order'),
    path('register/', RegisterView.as_view(), name='register'),
    path('recipe/', RecipeView.as_view(), name='recipe'),
    path('lk/', CabinetView.as_view(), name='lk'),
]
