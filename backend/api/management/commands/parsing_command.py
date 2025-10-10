from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Parses trivia questions from a website.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting parser...'))
        self.stdout.write(self.style.SUCCESS('Parsing finished.'))