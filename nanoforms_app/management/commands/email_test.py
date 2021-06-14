from django.core.mail import send_mail
from django.core.management import BaseCommand

from nanoforms.settings import DEFAULT_FROM_EMAIL, EMAIL_HOST, EMAIL_PORT


class Command(BaseCommand):
    help = 'Test email'

    def handle(self, *args, **options):
        print('EMAIL_HOST', EMAIL_HOST)
        print('EMAIL_PORT', EMAIL_PORT)
        print('DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL)
        send_mail(
            'Test mail subject',
            'Test mail body',
            DEFAULT_FROM_EMAIL,
            ['CHANGE_ME'],
            fail_silently=False,
        )
