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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from backend.views import (
    IndexView, AuthView, OrderView,
    RegisterView, RecipeView, CabinetView, PaymentSuccessView,
)


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('auth/', AuthView.as_view(), name='auth'),
    path('order/', login_required(OrderView.as_view()), name='order'),
    path('register/', RegisterView.as_view(), name='register'),
    path('recipe/', login_required(RecipeView.as_view()), name='recipe'),
    path('lk/', login_required(CabinetView.as_view()), name='lk'),
    path('yookassa/', login_required(PaymentSuccessView.as_view()), name='yookassa'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)