# FULLSTACK TEST PROJECT

## Stack:
- Next.js;
- Django;
- Nginx;
- Docker;

## Docker container startup commands:
### To run application in development mode:
    docker compose --env-file .env.dev --profile dev up --build
### To run application in production mode:
    docker compose --env-file .env.prod --profile prod up --build
### To stop application:
    docker compose --profile dev --profile prod --profile test --profile lint down
## Commands:
### To parse questions from https://www.triviawell.com/ use:
#### In development mode:
    docker compose --profile dev exec backend python manage.py parsing_command
#### In production mode:
     docker compose --profile prod exec backend python manage.py parsing_command
### To translate parsed questions:
#### In development mode:
    docker compose --profile dev exec backend python manage.py translate_questions
#### In production mode:
    docker compose --profile prod exec backend python manage.py translate_questions
#### You can change bastch size by adding batch-size parameter in the end
    docker compose --profile dev exec backend python manage.py translate_questions --batch-size 20
