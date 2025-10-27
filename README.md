# FULLSTACK TEST PROJECT

## Stack:
- Next.js;
- Django;
- Nginx;
- Docker;

## Docker container startup commands:
### To run application in development mode:
```bash
    docker compose --env-file .env.dev --profile dev up --build
```
### To run application in production mode:
```bash
    docker compose --env-file .env.prod --profile prod up --build
```
### To stop application:
```bash
    docker compose --profile dev --profile prod --profile test --profile lint down
```
### Ollama

This project uses the **Ollama** framework for language model processing.
You need to download **llama3.2:3b** language model before using the translation command.

#### Setup:

1. Start the Docker containers(development mode):
```bash
   docker compose --env-file .env.dev --profile test run --build backend-test
```

2. Download the model (the project uses **llama3.2:3b** by default, but you can use another):
```bash
   docker compose --env-file .env.dev --profile dev exec ollama ollama pull llama3.2:3b
```

3. Verify the model is loaded:
```bash
   docker compose --env-file .env.dev --profile dev exec ollama ollama list
```
## Tests:
### To run all backend tests:
    docker compose --env-file .env.dev --profile test run --build backend-test
### To run backend tests from a specific file you need to add the "_python manage.py test_" construction to the previous command:
    docker compose --env-file .env.dev --profile test run --build backend-test python manage.py test api.tests.test_api   

## Commands:
### To parse questions from https://www.triviawell.com/ use:
#### In development mode:
```bash
    docker compose --profile dev exec backend python manage.py parsing_command
```
#### In production mode:
```bash
     docker compose --profile prod exec backend python manage.py parsing_command
```
### To translate parsed questions:
#### In development mode:
```bash
    docker compose --profile dev exec backend python manage.py translate_questions
```
#### In production mode:
```bash
    docker compose --profile prod exec backend python manage.py translate_questions
```
#### You can change batch size by adding batch-size parameter in the end
```bash
    docker compose --profile dev exec backend python manage.py translate_questions --batch-size 20
```