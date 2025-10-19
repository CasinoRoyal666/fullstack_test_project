import json
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from api.models import Category, Question

class MockWebElement:
    def __init__(self, text=None, href=None, children_by_selector=None):
        self._text = text
        self._attributes = {"textContent": text, "href": href}
        self._children_by_selector = children_by_selector or {}

    def get_attribute(self, name):
        return self._attributes.get(name)

    def find_element(self, by, value):
        if by == By.CSS_SELECTOR and value in self._children_by_selector:
            return self._children_by_selector[value]
        raise NoSuchElementException(f"Element not found: {value}")

class ParsingCommandTests(TestCase):
    @patch.dict("os.environ", {"SELENIUM_URL": "http://localhost:4444/wd/hub"})
    @patch("api.management.commands.parsing_command.webdriver.Remote")
    @patch("api.management.commands.parsing_command.WebDriverWait")
    def test_parsing_command_success(self, mock_wait_class, mock_webdriver_remote):

        mock_card_1 = MockWebElement(children_by_selector={
            "a.text-inherit": MockWebElement(text="What is the capital of France?"),
            "li.list-inline-item a": MockWebElement(text="Geography"),
            "ul.d-none.answer li": MockWebElement(text="Paris"),
        })

        mock_card_2 = MockWebElement(children_by_selector={
            "a.text-inherit": MockWebElement(text="Who wrote 'Hamlet'?"),
            "li.list-inline-item a": MockWebElement(text="Literature"),
            "ul.d-none.answer li": MockWebElement(text="William Shakespeare"),
        })

        mock_driver = MagicMock()
        mock_webdriver_remote.return_value = mock_driver

        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        call_count = [0]

        def wait_until_side_effect(condition):
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutException("Cookie banner not found")
            elif call_count[0] == 2:
                return [mock_card_1, mock_card_2]
            else:
                raise TimeoutException("No more elements")

        mock_wait_instance.until.side_effect = wait_until_side_effect
        mock_driver.find_element.side_effect = NoSuchElementException("No 'Next' button")

        out = StringIO()
        call_command("parsing_command", stdout=out)

        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 2)

    @patch.dict("os.environ", {"SELENIUM_URL": "http://localhost:4444/wd/hub"})
    @patch("api.management.commands.parsing_command.webdriver.Remote")
    @patch("api.management.commands.parsing_command.WebDriverWait")
    def test_parsing_command_skip_without_category(self, mock_wait_class, mock_webdriver_remote):

        mock_card_no_category = MockWebElement(children_by_selector={
            "a.text-inherit": MockWebElement(text="Question without category"),
            "ul.d-none.answer li": MockWebElement(text="Answer"),
        })

        mock_driver = MagicMock()
        mock_webdriver_remote.return_value = mock_driver
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance
        call_count = [0]

        def wait_until_side_effect(condition):
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutException("Cookie banner not found")
            elif call_count[0] == 2:
                return [mock_card_no_category]
            else:
                raise TimeoutException("No more elements")

        mock_wait_instance.until.side_effect = wait_until_side_effect
        mock_driver.find_element.side_effect = NoSuchElementException("No 'Next' button")

        out = StringIO()
        call_command("parsing_command", stdout=out)

        self.assertEqual(Question.objects.count(), 0)
        self.assertIn("Skipping (no category)", out.getvalue())

    @patch.dict("os.environ", {"SELENIUM_URL": "http://localhost:4444/wd/hub"})
    @patch("api.management.commands.parsing_command.webdriver.Remote")
    @patch("api.management.commands.parsing_command.WebDriverWait")
    def test_parsing_command_skip_without_answer(self, mock_wait_class, mock_webdriver_remote):

        mock_card_no_answer = MockWebElement(children_by_selector={
            "a.text-inherit": MockWebElement(text="Question without answer"),
            "li.list-inline-item a": MockWebElement(text="Geography"),
        })

        mock_driver = MagicMock()
        mock_webdriver_remote.return_value = mock_driver
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance
        call_count = [0]

        def wait_until_side_effect(condition):
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutException("Cookie banner not found")
            elif call_count[0] == 2:
                return [mock_card_no_answer]
            else:
                raise TimeoutException("No more elements")

        mock_wait_instance.until.side_effect = wait_until_side_effect
        mock_driver.find_element.side_effect = NoSuchElementException("No 'Next' button")

        out = StringIO()
        call_command("parsing_command", stdout=out)

        self.assertEqual(Question.objects.count(), 0)
        self.assertIn("Skipping (no answer)", out.getvalue())

    @patch.dict("os.environ", {"SELENIUM_URL": "http://localhost:4444/wd/hub"})
    @patch("api.management.commands.parsing_command.webdriver.Remote")
    @patch("api.management.commands.parsing_command.WebDriverWait")
    def test_parsing_command_update_existing_question(self, mock_wait_class, mock_webdriver_remote):
        category = Category.objects.create(name="Geography")
        existing_question = Question.objects.create(
            text="What is the capital of France?",
            category=None,
            correct_answer=""
        )

        mock_card = MockWebElement(children_by_selector={
            "a.text-inherit": MockWebElement(text="What is the capital of France?"),
            "li.list-inline-item a": MockWebElement(text="Geography"),
            "ul.d-none.answer li": MockWebElement(text="Paris"),
        })

        mock_driver = MagicMock()
        mock_webdriver_remote.return_value = mock_driver
        mock_wait_instance = MagicMock()
        mock_wait_class.return_value = mock_wait_instance

        call_count = [0]

        def wait_until_side_effect(condition):
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutException("Cookie banner not found")
            elif call_count[0] == 2:
                return [mock_card]
            else:
                raise TimeoutException("No more elements")

        mock_wait_instance.until.side_effect = wait_until_side_effect
        mock_driver.find_element.side_effect = NoSuchElementException("No 'Next' button")

        out = StringIO()
        call_command("parsing_command", stdout=out)

        self.assertEqual(Question.objects.count(), 1)

        updated = Question.objects.get(text="What is the capital of France?")
        self.assertEqual(updated.correct_answer, "Paris")
        self.assertEqual(updated.category.name, "Geography")
        self.assertIn("Updated:", out.getvalue())


class TranslateQuestionsCommandTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Science")
        self.question = Question.objects.create(
            category=self.category,
            text="What is the chemical symbol for water?",
            correct_answer="H2O",
        )

    @patch("api.management.commands.translate_questions.OllamaLLM")
    @patch("api.management.commands.translate_questions.LLMChain")
    def test_translate_questions_success(self, mock_chain_class, mock_ollama):
        llm_response = json.dumps({
            "question_ru": "Какой химический символ у воды?",
            "answer_ru": "H2O",
            "pegi_rating": "3",
            "reasoning": "Basic science."
        })

        mock_chain_instance = MagicMock()
        mock_chain_instance.run.return_value = llm_response
        mock_chain_class.return_value = mock_chain_instance

        out = StringIO()
        call_command("translate_questions", "--batch-size", "1", stdout=out)

        self.question.refresh_from_db()
        self.assertEqual(self.question.translation_text, "Какой химический символ у воды?")
        self.assertEqual(self.question.pegi_rating, "3")

    @patch("api.management.commands.translate_questions.OllamaLLM")
    @patch("api.management.commands.translate_questions.LLMChain")
    def test_translate_questions_invalid_pegi(self, mock_chain_class, mock_ollama):

        llm_response = json.dumps({
            "question_ru": "Какой химический символ у воды?",
            "answer_ru": "H2O",
            "pegi_rating": "99",
            "reasoning": "Invalid PEGI"
        })

        mock_chain_instance = MagicMock()
        mock_chain_instance.run.return_value = llm_response
        mock_chain_class.return_value = mock_chain_instance

        out = StringIO()
        call_command("translate_questions", "--batch-size", "1", stdout=out)

        self.question.refresh_from_db()
        self.assertEqual(self.question.pegi_rating, "7")
        self.assertIn("Invalid PEGI", out.getvalue())

    @patch("api.management.commands.translate_questions.OllamaLLM")
    @patch("api.management.commands.translate_questions.LLMChain")
    def test_translate_questions_empty_translation(self, mock_chain_class, mock_ollama):

        llm_response = json.dumps({
            "question_ru": "",
            "answer_ru": "H2O",
            "pegi_rating": "3",
            "reasoning": "Empty translation"
        })

        mock_chain_instance = MagicMock()
        mock_chain_instance.run.return_value = llm_response
        mock_chain_class.return_value = mock_chain_instance

        out = StringIO()
        call_command("translate_questions", "--batch-size", "1", stdout=out)

        self.question.refresh_from_db()
        self.assertIsNone(self.question.translation_text)
        self.assertIn("Empty translation received", out.getvalue())

    @patch("api.management.commands.translate_questions.OllamaLLM")
    @patch("api.management.commands.translate_questions.LLMChain")
    def test_translate_questions_invalid_json(self, mock_chain_class, mock_ollama):

        llm_response = "This is not JSON at all"

        mock_chain_instance = MagicMock()
        mock_chain_instance.run.return_value = llm_response
        mock_chain_class.return_value = mock_chain_instance

        out = StringIO()
        call_command("translate_questions", "--batch-size", "1", stdout=out)

        self.question.refresh_from_db()
        self.assertIsNone(self.question.translation_text)
        self.assertIn("No valid JSON found", out.getvalue())