docker run --rm --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres

docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management

docker run -it --rm --name redis -p 6379:6379 redis

celery -A myshop worker -l info

celery -A myshop flower

stripe listen --forward-to 127.0.0.1:8000/payment/webhook/