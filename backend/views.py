from datetime import timedelta
import email
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone


from backend.models import Type, Allergy, User, Recipe, RecipeShow, Order


class IndexView(TemplateView):
    template_name = "index.html"


class AuthView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('logout'):
            logout(request)
        return render(request, "auth.html")

    def post(self, request):
        print(request.POST)
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)
        print(user)
        if user:
            login(request, user)
            return redirect('/lk/')

        return render(request, "auth.html", context={
            'error': 'Пожалуйста введите корректные логин и пароль'
        })


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
        order = Order(
            user=request.user,
            persons=request.POST.get('persons'),
            calories=request.POST.get('calories'),
            price=request.POST.get('price'),
            finish_time=timezone.now() + timedelta(days=int(request.POST.get('length'))*30)
        )
        order.save()
        for type in Type.objects.all():
            if request.POST.get(type.name) != '0':
                order.types.add(type)
        for allergy in Allergy.objects.all():
            if request.POST.get(allergy.name):
                order.allergies.add(allergy)
        print(order)
        return redirect('/lk')


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
            return redirect('/lk/')
        print(user)
        return redirect('/')


class RecipeView(View):
    def get(self, request, *args, **kwargs):
        # получаем активную подписку
        order = request.user.orders.filter(
            start_time__lte=timezone.now(), finish_time__gte=timezone.now()
            ).last()
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
        print(recipes_shown_today['calories'])
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
            recipe = recipe_never_shown.last()
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
            context={
                'name': recipe.name,
                'calories': recipe.calories,
                'ingredients': recipe.ingreds,
                'content': recipe.content,
            }
        )


class CabinetView(View):
    def get(self, request):
        if not request.user.id:
            return redirect('/auth/')
        order = Order.objects.filter(user__id=request.user.id).filter(finish_time__gte=timezone.now()).last()
        if not order:
            return render(request, 'lk.html')
        context = {
            'types': [type.name for type in order.types.all()],
            'allergies': [allergy.name for allergy in order.allergies.all()],
            'menus': [menu.name for menu in order.menus.all()],
            'persons': order.persons,
            'calories': order.calories,
            'finish_time': order.finish_time,
        }
        return render(request, 'lk.html', context=context)

    def post(self, request):
        if not request.user.id:
            return redirect('/auth/')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = request.user
        if name:
            user.name = name
        if email:
            user.email = email
        if password:
            user.set_password(password)
        user.save()
        return self.get(request)
