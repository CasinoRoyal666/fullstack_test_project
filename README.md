# FULLSTACK TEST PROJECT

## Stack:
- REACT
- REDUX
- DJANGO
- DOCKER

## Docker container startup commands:
### To run application in development mode:
    docker compose --env-file .env.dev --profile dev up --build
### To run application in production mode:
    docker compose --env-file .env.prod --profile prod up --build
### To stop application:
    docker compose --profile dev --profile prod --profile test --profile lint down



