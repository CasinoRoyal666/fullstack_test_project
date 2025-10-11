import os
import time

from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from api.models import Question, Category


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
        driver = None
        try:
            self.stdout.write(f'Connecting to Selenium at {selenium_url}')
            driver = webdriver.Remote(
                command_executor=RemoteConnection(selenium_url, keep_alive=False),
                options=chrome_options
            )
            self.stdout.write(self.style.SUCCESS('Successfully connected to Selenium.'))
            page_number = 1
            MAX_PAGES_TO_PARSE = 4
            target_url = "https://www.triviawell.com/"
            self.stdout.write(f'Opening {target_url}...')
            driver.get(target_url)
            wait = WebDriverWait(driver, 10)
            try:
                cookie_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a:has(span#cmpbntyestxt)")))
                self.stdout.write("Cookie banner found. Clicking 'Accept All'.")
                cookie_button.click()
                time.sleep(2)
            except TimeoutException:
                self.stdout.write("Cookie banner not found or already accepted.")
            while page_number <= MAX_PAGES_TO_PARSE:
                try:
                    question_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card.mb-4.card-hover")))
                except TimeoutException:
                    self.stdout.write(self.style.SUCCESS("No more questions found. Finishing parsing."))
                    break

                for card in question_cards:
                    try:
                        question_text_element = card.find_element(By.CSS_SELECTOR, "a.text-inherit")
                        text = question_text_element.get_attribute('textContent').strip()

                        if Question.objects.filter(text=text).exists():
                            self.stdout.write(f'Question "{text[:50]}..." already exists. Skipping.')
                            continue

                        category_tags = card.find_elements(By.CSS_SELECTOR, "li a")
                        if not category_tags:
                            self.stdout.write(self.style.WARNING(f'No category found for question: "{text[:50]}..."'))
                            continue

                        main_category_name = category_tags[0].text
                        category, _ = Category.objects.get_or_create(name=main_category_name)
                        correct_answer = card.find_element(By.CSS_SELECTOR, "ul.d-none.answer li").text

                        Question.objects.create(
                            category=category,
                            text=text,
                            correct_answer=correct_answer
                        )
                        self.stdout.write(self.style.SUCCESS(f'Saved question: "{text[:50]}..."'))
                    except NoSuchElementException as e:
                        self.stdout.write(self.style.WARNING(f'Could not parse a card, missing element: {e}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'An unexpected error occurred for a card: {e}'))
                try:
                    next_page_link = driver.find_element(By.XPATH, '//a[text()="Next"]')
                    next_page_url = next_page_link.get_attribute('href')

                    if next_page_url:
                        self.stdout.write(f"Navigating to next page: {next_page_url}")
                        driver.get(next_page_url)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.card.mb-4.card-hover")))
                        page_number += 1
                        time.sleep(1)
                    else:
                        self.stdout.write(self.style.SUCCESS("No 'Next' button found. This is the last page."))
                        break
                except NoSuchElementException:
                    self.stdout.write(self.style.SUCCESS("No 'Next' button found. This is the last page."))
                    break
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'A critical error occurred: {e}'))
        finally:
            if driver:
                driver.quit()
                self.stdout.write(self.style.SUCCESS('Browser session closed.'))
        self.stdout.write(self.style.SUCCESS('Parsing finished.'))


        #     category_urls = [elem.get_attribute('href') for elem in category_elements]
        #     self.stdout.write(f'found {len(category_urls)} categories')
        #
        #     for url in category_urls:
        #         driver.get(url)
        #         category_name_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
        #         category_name = category_name_element.text
        #         category, created =  Category.objects.get_or_create(name=category_name)
        #         if created:
        #             self.stdout.write(self.style.SUCCESS(f'Category "{category_name}" created.'))
        #         else:
        #             self.stdout.write(f'Category "{category_name}" already exists.')
        #         question_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, )))
        #         self.stdout.write(f'Found {len(question_cards)} questions on the page.')
        #         for card in question_cards:
        #             try:
        #                 text = card.find_element(By.CSS_SELECTOR, ).text
        #                 answer_options = [opt.text for opt in card.find_elements(By.CSS_SELECTOR, )]
        #                 correct_answer = card.find_element(By.CSS_SELECTOR, ).text
        #                 if text and correct_answer and len(answer_options) > 0:
        #                     Question.object.create(
        #                         category=category,
        #                         text=text,
        #                         answer_options={'options': answer_options},
        #                         correct_answer=correct_answer,
        #                     )
        #                     self.stdout.write(f'  - Saved question: "{text[:50]}..."')
        #             except Exception as e:
        #                 self.stdout.write(self.style.WARNING(f'Could not parse a question card: {e}'))
        #         time.sleep(1)
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
        # finally:
        #     if driver:
        #         driver.quit()
        #         self.stdout.write(self.style.SUCCESS('Browser session closed.'))
        # self.stdout.write(self.style.SUCCESS('Parsing finished.'))



