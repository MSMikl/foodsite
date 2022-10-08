from datetime import timedelta
import email

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.models import User, Order

class Command(BaseCommand):
    help = 'Проверка истекающей подписки и рассылка уведомлений'

    def send_email(self, email):
        print(email)

    def handle(self, *args, **options):
        nowadays = timezone.now().date()
        finishing_orders = Order.objects.filter(finish_time=(nowadays + timedelta(days=4)))
        for order in finishing_orders:
            self.send_email(order.user.email)

        finished_orders = Order.objects.filter(finish_time=(nowadays - timedelta(days=1)))
