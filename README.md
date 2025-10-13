# FULLSTACK TEST PROJECT

## Stack:
- Next.js;
- Django;
- Nginx;
- Docker;

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
