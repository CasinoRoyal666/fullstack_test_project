# FULLSTACK TEST PROJECT

## Stack:
- Next.js;
- Django;
- Nginx;
- Docker;

## Getting started
This project is fully containerized using Docker and is designed to run in two distinct modes:
- development;
- production;
### Prerequisites
To run this project on your computer you must have:
- Docker and Docker Compose;
- Docker Daemon running;
### 1) Environment Setup
You need to configure the environment variables for both modes
1) For development mode copy .env.dev.example to new .env.dev file and configurate
2) For production mode copy .env.prod.example to new .env.prod file and configurate
### 2) Running the app
To **run** application in **development mode** in root directory write:

    docker compose --env-file .env.dev --profile dev up --build

To **run** application in **production mode** in root directory write:

    docker compose --env-file .env.prod --profile prod up --build

To **stop** application in root directory write:

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
