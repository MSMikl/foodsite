from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail

from backend.models import Order


class Command(BaseCommand):
    help = 'Проверка истекающей подписки и рассылка уведомлений'

    def send_email(self, text, email, subject='foodsite notification'):
        send_mail(
            subject,
            text,
            'foodsite@foodsite.michalbl4.ru',  # from_address
            [email],
            fail_silently=True,
        )

    def handle(self, *args, **options):
        nowadays = timezone.now().date()
        finishing_orders = Order.objects.filter(finish_time=(nowadays + timedelta(days=4)))
        for order in finishing_orders:
            self.send_email('Ваша подписка истекает через 4 дня', order.user.email)

        finished_orders = Order.objects.filter(finish_time=(nowadays - timedelta(days=1)))
        for order in finished_orders:
            self.send_email('Ваша подписка истекла', order.user.email)
