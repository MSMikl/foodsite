import datetime

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


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
    name = models.CharField('Название', max_length=150, blank=False)
    content = models.TextField('Состав', blank=False)
    calories = models.IntegerField('Калорийность', null=False, blank=False)
    allergies = models.ManyToManyField(Allergy, related_name='recipes', verbose_name='Аллергии')
    menus = models.ManyToManyField(Menu, related_name='recipes', verbose_name='Типы меню')
    image = models.ImageField('Изображение')

    def __str__(self) -> str:
        return self.name


    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Клиент')
    types = models.ManyToManyField(Type, related_name='orders', verbose_name='Приемы пищи')
    menus = models.ManyToManyField(Menu, related_name='orders', verbose_name='Меню')
    allergies = models.ManyToManyField(Allergy, related_name='orders', verbose_name='Аллергии')
    persons = models.IntegerField('Количество персон', default=1)
    calories = models.IntegerField('Калории', null=False, blank=False)
    price = models.DecimalField('Цена', null=False, blank=False, decimal_places=0, max_digits=6)
    start_time = models.DateField('Дата начала', auto_now_add=True)
    finish_time = models.DateField('Дата окончания', null=False, blank=False)

    def __str__(self) -> str:
        return f'Подписка {self.id}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
