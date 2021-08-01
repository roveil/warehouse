# Микросервис синхронизации CSV-файла с продуктами

## Что делает?
* Синхронизирует файл в облаке с текущей БД, используя celery-beat для планирования задачи и celery-worker для
ее выполнения
* Предоставляет API для доступа к данным:
```
producers/ - GET. Получить всех производителей (используется пагинация)
producer/<product_id>/products - GET. Получить все продукты данного производителя (используется пагинация) 
```

## Установка

* Установить [Docker](https://docs.docker.com/engine/install/ubuntu/) и 
[docker-compose](https://docs.docker.com/compose/install/):

* Запустить микросервис используя следующую команду

  ```shell
  DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose --compatibility up --build --force-recreate --detach \
  --scale base=0 --scale app=1 --scale worker=1 --scale worker-beat=1
  ```
##### Переменные окружения находятся в файле .env

Переменные окружения
--------------

* `SECRET_KEY`  
  **Default:** `no-secret-key`    
  
* `DEBUG`  
  **Default:** `False`  
    
* `ACCESS_TOKEN`  
  **Default:** ``  
  Токен доступа для запросов по API
  
* `CELERY_QUEUE`
  **Default:** `warehouse_main`
  Очередь, которая будет использоваться для синхронизации данных
  
* `SENTRY_SDK_DSN_URL`
  **Default:** ``
  Проект в сентри, для логирования ошибок

* `GOOGLE_DOCS_DOCUMENT_URL`
  **Default:** ``
  Ссылка на google-таблицу csv с данными для синхронизации

* `BROKER_URL`
  **Default:** `amqp://`
  Celery-параметер. url - с типом транспорта до сервера, который будет использоваться в качестве сервера очередей

* `DB_HOST`
  **Default:** `localhost`
  Хост базы данных Postgres

* `DB_PORT`
  **Default:** `5432`
  TCP-порт, на котором слушает POSTGRES

* `DB_NAME`
  **Default:** `warehouse_db`
  Имя БД
  
* `DB_USER`
  **Default:** `warehouse_user`
  Пользователь, от имени которого будет работать django-приложение

* `DB_PASSWORD`
  **Default:** `warehouse_pass`
  Пароль пользователя
 
###### еще можно изменять параметры воркеров - их можно посмотреть в docker-entrypoint.sh
