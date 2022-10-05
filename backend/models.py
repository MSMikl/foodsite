import datetime
from django.db import models
from django.contrib.auth.models import User


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
    lenght = models.IntegerField('Продолжительность подписки в днях', null=False, blank=False)

    def __str__(self) -> str:
        return f'Подписка {self.id}'

    def finish_time(self):
        return self.start_time + datetime.timedelta(days=self.lenght)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
