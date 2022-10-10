import datetime
import json

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.html import mark_safe


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, is_staff=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True)
    name = models.CharField('Имя', max_length=100, blank=True)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    is_active = models.BooleanField('Активный', default=True)
    is_staff = models.BooleanField('Менеджер', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Allergy(models.Model):
    name = models.CharField('Название', max_length=100, blank=False)
    description = models.TextField('Описание', blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Аллергия'
        verbose_name_plural = 'Аллергии'


class Menu(models.Model):
    name = models.CharField('Название', max_length=100, blank=False)
    description = models.TextField('Описание', blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Тип меню'
        verbose_name_plural = 'Типы меню'


class Type(models.Model):
    name = models.CharField('Название', max_length=150, blank=False)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', default=0, decimal_places=0, max_digits=6)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Прием пищи'
        verbose_name_plural = 'Приемы пищи'


class Recipe(models.Model):
    name = models.CharField('Название', max_length=150)
    content = models.TextField('Инструкция')
    ingredients = models.TextField(
        verbose_name='Ингредиенты',
        blank=True,
    )
    calories = models.IntegerField('Калорийность')
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        related_name='recipes',
        verbose_name='Аллергии'
    )
    menus = models.ManyToManyField(
        Menu,
        blank=True, 
        related_name='recipes',
        verbose_name='Типы меню'
    )
    image = models.ImageField('Изображение', null=True, blank=True)

    def image_tag(self):
            return mark_safe(f'<img src="/media/{self.image}" style="max-width:150px;max-height:150px;height:auto;width:auto"/>')

    image_tag.short_description = 'Картинка'

    def set_ingredients(self, ingredients):
        self.ingredients = json.dumps(ingredients)

    def get_ingredients(self):
        return json.loads(self.ingredients)

    def del_ingredients(self):
        del self.ingredients

    ingreds = property(get_ingredients, set_ingredients, del_ingredients, "Ingreds")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Клиент'
    )
    types = models.ManyToManyField(Type, related_name='orders', verbose_name='Приемы пищи')
    menus = models.ManyToManyField(Menu, blank=True, related_name='orders', verbose_name='Меню')
    allergies = models.ManyToManyField(Allergy, blank=True, related_name='orders', verbose_name='Аллергии')
    persons = models.IntegerField('Количество персон', default=1)
    calories = models.IntegerField('Калории')  # Калории на всех persons в день (не на 1 человека)
    price = models.DecimalField('Цена', decimal_places=0, max_digits=6)
    start_time = models.DateField('Дата начала', auto_now_add=True)
    finish_time = models.DateField('Дата окончания')
    is_active = models.BooleanField('Действует', default=False)

    def __str__(self) -> str:
        return f'Подписка {self.id}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class RecipeShow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shows', verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shows', verbose_name='Рецепт')
    date = models.DateField('Дата показа', auto_now_add=True)

    class Meta:
        verbose_name = 'Показ'
        verbose_name_plural = 'Показы'


class YookassaPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='Подписка')
    payment_id = models.CharField('Идентификатор', max_length=40, db_index=True)
    is_pending = models.BooleanField('Ожидает оплаты', default=True)


class Referer(models.Model):
    referer = models.TextField('Источник')
    date = models.DateField('Дата показа', auto_now_add=True)
