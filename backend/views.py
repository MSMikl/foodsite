import email
from django.contrib.auth import authenticate, login
from django.db.models import Count, Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from backend.models import Type, Allergy, User, Recipe, RecipeShow


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


class RecipeView(View):
    def get(self, request, *args, **kwargs):
        # получаем активную подписку
        order = request.user.orders.filter(
            start_time__lte=timezone.now(), finish_time__gte=timezone.now()
            ).first()
        if not order:
            return render(request,
                          template_name='recipe.html',
                          context={'error': 'Нет активных подписок'})

        eat_times = order.types.count()

        # проверяем лимит рецептов
        recipes_shown_today = RecipeShow.objects\
            .filter(user=request.user, date=timezone.now().date())\
            .aggregate(count=Count('id'), calories=Sum('recipe__calories'))
        eat_times_remain = eat_times - recipes_shown_today['count']
        if eat_times_remain < 1:
            return render(
                request,
                template_name='recipe.html',
                context={'error': 'На сегодня лимит рецептов исчерпан'}
                )
        calories_remain = order.calories / order.persons
        if recipes_shown_today['calories']:
            calories_remain -= recipes_shown_today['calories']

        # фильтруем по аллергии
        recipes = Recipe.objects.exclude(allergies__in=order.allergies.all())

        # фильтруем по калориям
        recipes = recipes.filter(
            calories__lte=calories_remain / eat_times_remain * 1.2
            )
        recipes = recipes.filter(
            calories__gte=calories_remain / eat_times_remain * 0.8
            )
        if not recipes:
            return render(
                request,
                template_name='recipe.html',
                context={'error': 'Нет подходящих рецептов'}
            )

        # ищем ни разу не показанные рецепты
        recipe_never_shown = recipes.exclude(
            shows__in=RecipeShow.objects.filter(user=request.user)
        )
        if recipe_never_shown:
            recipe = recipe_never_shown
            print('never', recipe)
        else:
            # ищем самый ранний из показанных
            earliest_show = RecipeShow.objects\
                .filter(user=request.user, recipe__in=recipes)\
                .earliest('date')
            recipe = earliest_show.recipe
        return render(
            request,
            template_name='recipe.html',
            context={'recipe': recipe}
        )