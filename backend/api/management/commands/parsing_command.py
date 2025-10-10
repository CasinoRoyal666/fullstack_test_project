import os
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import RemoteConnection

class Command(BaseCommand):
    help = 'Parses trivia questions from a website.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting parser...'))
        selenium_url = os.environ.get('SELENIUM_URL')
        if not selenium_url:
            self.stdout.write(self.style.ERROR('SELENIUM_URL .env variable not set'))
            return
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        try:
            self.stdout.write(f'Connecting to Selenium at {selenium_url}')
            driver = webdriver.Remote(
                command_executor=RemoteConnection(selenium_url, keep_alive=False),
                options=chrome_options
            )
            self.stdout.write(self.style.SUCCESS('Successfully connected to Selenium.'))

            target_url = "https://www.triviawell.com/"
            self.stdout.write(f'Opening {target_url}...')
            driver.get(target_url)
            self.stdout.write(self.style.SUCCESS(f'Page title: {driver.title}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR - {e}'))
        finally:
            if 'driver' in locals() and driver:
                driver.quit()
                self.stdout.write(self.style.SUCCESS('Session closed'))
        self.stdout.write(self.style.SUCCESS('Parsing finished.'))