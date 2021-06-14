from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Cromwell cleanup'

    def handle(self, *args, **options):
        pass
