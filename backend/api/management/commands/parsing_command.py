import os
import time

from api.models import Category, Question
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Command(BaseCommand):
    help = "Parses trivia questions from a website."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting parser..."))
        selenium_url = os.environ.get("SELENIUM_URL")
        if not selenium_url:
            self.stdout.write(self.style.ERROR(".env variable not set"))
            return
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = None
        try:
            self.stdout.write(f"Connecting to Selenium at {selenium_url}")
            driver = webdriver.Remote(
                command_executor=RemoteConnection(selenium_url, keep_alive=False),
                options=chrome_options,
            )
            self.stdout.write(self.style.SUCCESS("Successfully connected to Selenium."))
            page_number = 1
            MAX_PAGES_TO_PARSE = 100
            target_url = "https://www.triviawell.com/"
            self.stdout.write(f"Opening {target_url}...")
            driver.get(target_url)
            wait = WebDriverWait(driver, 10)
            try:
                cookie_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a:has(span#cmpbntyestxt)")
                    )
                )
                self.stdout.write("Cookie banner found. Clicking 'Accept All'.")
                cookie_button.click()
                time.sleep(2)
            except TimeoutException:
                self.stdout.write("Cookie banner not found or already accepted.")

            while page_number <= MAX_PAGES_TO_PARSE:
                try:
                    question_cards = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div.card.mb-4.card-hover")
                        )
                    )
                except TimeoutException:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "No more questions found. Finishing parsing."
                        )
                    )
                    break

                for card in question_cards:
                    try:
                        question_text_element = card.find_element(
                            By.CSS_SELECTOR, "a.text-inherit"
                        )
                        text = question_text_element.get_attribute(
                            "textContent"
                        ).strip()

                        existing_question = Question.objects.filter(text=text).first()

                        category_name = None
                        try:
                            category_element = card.find_element(
                                By.CSS_SELECTOR, "li.list-inline-item a"
                            )
                            category_name = category_element.get_attribute(
                                "textContent"
                            ).strip()

                            if category_name:
                                self.stdout.write(f'Category: "{category_name}"')
                            else:
                                self.stdout.write(
                                    self.style.WARNING("Empty category name")
                                )
                        except NoSuchElementException:
                            self.stdout.write(
                                self.style.WARNING("No category element found")
                            )

                        correct_answer = None
                        try:
                            answer_element = card.find_element(
                                By.CSS_SELECTOR, "ul.d-none.answer li"
                            )
                            correct_answer = answer_element.get_attribute(
                                "textContent"
                            ).strip()

                            if correct_answer:
                                self.stdout.write(f'Answer: "{correct_answer[:60]}..."')
                            else:
                                self.stdout.write(
                                    self.style.WARNING("Empty answer text")
                                )
                        except NoSuchElementException:
                            self.stdout.write(
                                self.style.WARNING("No answer element found")
                            )

                        if existing_question:
                            needs_update = False

                            current_cat_empty = (
                                not existing_question.category
                                or not existing_question.category.name
                            )

                            if current_cat_empty and category_name:
                                category, _ = Category.objects.get_or_create(
                                    name=category_name
                                )
                                existing_question.category = category
                                needs_update = True
                                self.stdout.write(
                                    f'Updated category to: "{category.name}"'
                                )

                            if not existing_question.correct_answer and correct_answer:
                                existing_question.correct_answer = correct_answer
                                needs_update = True
                                self.stdout.write("Updated answer")

                            if needs_update:
                                existing_question.save()
                                self.stdout.write(
                                    self.style.SUCCESS(f'Updated: "{text[:50]}..."')
                                )
                            else:
                                self.stdout.write(f'Already complete: "{text[:50]}..."')
                            continue

                        if not category_name:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Skipping (no category): "{text[:50]}..."'
                                )
                            )
                            continue

                        if not correct_answer:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Skipping (no answer): "{text[:50]}..."'
                                )
                            )
                            continue

                        category, _ = Category.objects.get_or_create(name=category_name)
                        Question.objects.create(
                            category=category, text=text, correct_answer=correct_answer
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'Saved: "{text[:50]}..."')
                        )

                    except NoSuchElementException as e:
                        self.stdout.write(
                            self.style.WARNING(f"Could not parse card: {e}")
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Unexpected error: {e}"))

                try:
                    next_page_link = driver.find_element(By.XPATH, '//a[text()="Next"]')
                    next_page_url = next_page_link.get_attribute("href")

                    if next_page_url:
                        self.stdout.write(
                            f"\n→ Page {page_number + 1}: {next_page_url}\n"
                        )
                        driver.get(next_page_url)
                        wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "div.card.mb-4.card-hover")
                            )
                        )
                        page_number += 1
                        time.sleep(1)
                    else:
                        self.stdout.write(self.style.SUCCESS("No next page URL."))
                        break
                except NoSuchElementException:
                    self.stdout.write(self.style.SUCCESS("No 'Next' button found."))
                    break

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical error: {e}"))
        finally:
            if driver:
                driver.quit()
                self.stdout.write(self.style.SUCCESS("Browser closed."))

        total = Question.objects.count()
        with_categories = Question.objects.filter(category__isnull=False).count()
        with_answers = Question.objects.exclude(correct_answer="").count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n"
                f"===== PARSING FINISHED =====\n"
                f"Total questions: {total}\n"
                f"With categories: {with_categories}\n"
                f"With answers: {with_answers}\n"
                f"============================"
            )
        )
