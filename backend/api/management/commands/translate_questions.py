import json
import os
import time

from api.models import Question
from django.core.management.base import BaseCommand
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


class Command(BaseCommand):
    help = "Translating to RUS and assigning PEGI rating"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,
            help="Number of questions to process in one batch (default: 10)",
        )
        parser.add_argument(
            "--model", type=str, default="llama3.2:3b", help="Ollama model to use"
        )
        parser.add_argument(
            "--all", action="store_true", help="Translate all remaining questions"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting translation with LangChain..."))
        ollama_url = os.environ.get("OLLAMA_URL", "http://ollama:11434")
        model_name = options["model"]
        batch_size = options["batch_size"]
        translate_all = options["all"]

        self.stdout.write("Conf:")
        self.stdout.write(f"Ollama URL: {ollama_url}")
        self.stdout.write(f"Batch size: {batch_size}")
        if translate_all:
            self.stdout.write("Translate all remaining questions")

        try:
            llm = OllamaLLM(
                base_url=ollama_url,
                model=model_name,
                temperature=0.3,
                num_predict=512,
            )
            self.stdout.write(self.style.SUCCESS("LangChain init"))
            self.stdout.write(self.style.SUCCESS("Successful connection to Ollama"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to init LangChain: {e}"))
            return

        prompt_template = PromptTemplate(
            input_variables=["question", "answer", "category"],
            template="""You are a professional translator and content moderator.

Task 1: Translate the English trivia question and answer to natural, fluent Russian.
Task 2: Assign a PEGI age rating (3, 7, 12, 16, or 18) based on content appropriateness.

Question: {question}
Correct Answer: {answer}
Category: {category}

PEGI Rating Guidelines:
- 3: Suitable for all ages, no inappropriate content whatsoever
- 7: Mild fantasy violence, mild scary content, very mild bad language
- 12: Moderate violence, mild bad language, suggestive themes, gambling references
- 16: Strong violence, strong language, sexual references, drug/alcohol references
- 18: Extreme violence, explicit sexual content, hard drugs, strong encouragement of gambling  # noqa: E501

Respond ONLY in this exact JSON format (no markdown, no extra text, no code blocks):
{{
  "question_ru": "Russian translation of the question here",
  "answer_ru": "Russian translation of the answer here",
  "pegi_rating": "7",
  "reasoning": "Brief explanation in English why this rating was assigned"
}}
""",
        )

        chain = LLMChain(llm=llm, prompt=prompt_template)

        if translate_all:
            batch_number = 0
            total_session_success = 0

            while True:
                remaining = Question.objects.filter(
                    translation_text__isnull=True
                ).count()

                if remaining == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"\nAll questions translated! Total in session: {total_session_success}"
                        )
                    )
                    break

                batch_number += 1
                self.stdout.write(
                    f"\n--- Batch #{batch_number} | Remaining: {remaining} ---"
                )

                success = self.process_batch(chain, batch_size, model_name)
                total_session_success += success

                time.sleep(3)
        else:
            self.process_batch(chain, batch_size, model_name)

    def process_batch(self, chain, batch_size, model_name):
        questions = Question.objects.filter(translation_text__isnull=True).order_by(
            "id"
        )[:batch_size]
        total = questions.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No questions to translate"))
            return 0

        self.stdout.write(f"\nFound {total} questions to translate\n")
        self.stdout.write("=" * 80)

        success_count = 0
        error_count = 0
        for idx, question in enumerate(questions, 1):
            self.stdout.write(
                f"\n[{idx}/{total}] Processing question ID: {question.id}"
            )
            self.stdout.write(f'EN: "{question.text[:70]}..."')

            try:
                result = chain.run(
                    question=question.text,
                    answer=question.correct_answer,
                    category=question.category.name if question.category else "General",
                )

                try:
                    json_start = result.find("{")
                    json_end = result.find("}") + 1

                    if json_start != -1 and json_end > json_start:
                        json_str = result[json_start:json_end]
                        data = json.loads(json_str)

                        question_ru = data.get("question_ru", "").strip()
                        answer_ru = data.get("answer_ru", "").strip()
                        pegi_rating = data.get("pegi_rating", "7").strip()
                        reasoning = data.get("reasoning", "N/A")

                        if not question_ru or not answer_ru:
                            self.stdout.write(
                                self.style.WARNING("Empty translation received!!!!!")
                            )
                            error_count += 1
                            continue

                        valid_pegi = ["3", "7", "12", "16", "18"]
                        if pegi_rating not in valid_pegi:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Invalid PEGI "{pegi_rating}" (default to "7")'
                                )
                            )
                            pegi_rating = "7"

                        question.translation_text = question_ru
                        question.correct_answer_ru = answer_ru
                        question.pegi_rating = pegi_rating
                        question.save()

                        self.stdout.write(self.style.SUCCESS("Translation successful!"))
                        self.stdout.write(f'  RU: "{question_ru[:70]}..."')
                        self.stdout.write(f'  Answer RU: "{answer_ru[:50]}..."')
                        self.stdout.write(f"  PEGI: {pegi_rating}+ - {reasoning}")
                        success_count += 1

                    else:
                        self.stdout.write(
                            self.style.WARNING("No valid JSON found in response")
                        )
                        self.stdout.write(f"Response preview: {result[:150]}...")
                        error_count += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
                    error_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Chain execution error: {e}"))
                error_count += 1

        self.stdout.write("\n" + "=" * 80)

        translated_total = Question.objects.filter(
            translation_text__isnull=False
        ).count()
        total_questions = Question.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"TRANSLATION FINISHED \n"
                f"\n"
                f"This Session:\n"
                f"  - Successful: {success_count}\n"
                f"  - Errors: {error_count}\n"
                f"\n"
                f"Database Stats:\n"
                f"  - Total questions: {total_questions}\n"
                f"  - Translated: {translated_total}\n"
                f"  - Remaining: {total_questions - translated_total}\n"
            )
        )

        return success_count
