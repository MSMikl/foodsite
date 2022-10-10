import json
from datetime import timedelta, datetime
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum,  Max
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone
from yookassa import Payment

from backend.models import (
    Type, Allergy, User, Recipe, RecipeShow, Order,
    YookassaPayment, Referer,
)


class IndexView(View):
    def get(self, request, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER')
        if referer:
            Referer.objects.create(referer=referer)
        if request.GET.get('logout'):
            logout(request)
        return render(request, "index.html")


class AuthView(View):
    def get(self, request, *args, **kwargs):
        if request.GET.get('logout'):
            logout(request)
        return render(request, "auth.html", context={
            'next': request.GET.get('next', 'index'),
        })

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        next = request.POST.get('next', 'lk')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect(next)

        return render(request, "auth.html", context={
            'error': 'Пожалуйста введите корректные логин и пароль'
        })


class OrderView(View):
    def create_payment(self, amount):
        payment = Payment.create(
            {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://foodsite.michalbl4.ru/yookassa/"
                },
                "description": "Оплата подписки Foodsite"
            }
        )
        return payment.id, payment.confirmation.confirmation_url

    def get(self, request):
        types = [{
            'id': type.id,
            'title': type.name,
            'price': type.price
        } for type in Type.objects.all()]

        allergies = [{
            'title': allergy.name,
            'id': allergy.id,
            } for allergy in Allergy.objects.all()]
        return render(request, 'order.html', context={
            'types': types,
            'allergies': allergies
        })

    def post(self, request):
        payment_id, payment_url = self.create_payment(request.POST.get('price'))
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
        YookassaPayment.objects.create(order=order, payment_id=payment_id)
        return redirect(payment_url)


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
        return redirect('/')


class RecipeView(View):
    def get(self, request, *args, **kwargs):
        if not request.GET.get('getnew'):  # запрос без параметров - выдаем рецепт из истории
            try:
                last_show = RecipeShow.objects.filter(user=request.user).select_related().latest(
                    'date'
                    )
            except RecipeShow.DoesNotExist:
                last_show = None
            if last_show:
                context={
                    'recipe': last_show.recipe,
                }
            else:
                context = {
                    'error_first_recipe': 'Вы еще не получали рецепты. Начните прямо сейчас!'
                }
            return render(
                request,
                template_name='recipe.html',
                context=context
            )

        # запрос с параметром .../recipe?getnew=true - выдаем новый рецепт
        # получаем активную подписку
        order = request.user.orders.filter(
            start_time__lte=timezone.now(),
            finish_time__gte=timezone.now(),
            is_active=True,
            ).last()
        if not order:
            return render(request,
                          template_name='recipe.html',
                          context={'error_no_subscribes': 'Нет активных подписок'})
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
                context={'error_recipes_finished': 'На сегодня лимит рецептов исчерпан'}
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
            recipe = recipe_never_shown.last()
        else:
            # ищем самый ранний по последнему показу
            recipe = recipes.prefetch_related('shows')\
                .values('id', 'name', 'content', 'calories', 'image',
                        last_show=Max('shows__date')
                        )\
                .order_by('last_show')\
                .first()

        RecipeShow.objects.create(recipe_id=recipe.id, user=request.user)
        return render(
            request,
            template_name='recipe.html',
            context={
                'recipe': recipe,
            }
        )


class CabinetView(View):
    def get(self, request):
        if not request.user.id:
            return redirect('/auth/')
        order = Order.objects.filter(user__id=request.user.id, is_active=True).filter(finish_time__gte=timezone.now()).select_related().last()
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


class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.id:
            return redirect('/auth/')
        payments = YookassaPayment.objects.filter(
            order__in=request.user.orders.all(), is_pending=True
        )
        for payment in payments:
            payment_info = Payment.find_one(payment.payment_id)
            if payment_info.paid:
                payment.is_pending = False
                payment.save()
                payment.order.is_active = True
                payment.order.save()
            elif datetime.strptime(
                    payment_info.expires_at,
                    "%Y-%m-%dT%H:%M:%S.%fZ"
            ) < datetime.now():
                payment.update(is_pending=False)
        return redirect('/lk')
