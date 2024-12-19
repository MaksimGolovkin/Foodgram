![Workflow Status](https://github.com/MaksimGolovkin/foodgram/actions/workflows/main.yml/badge.svg)

# Проект Foodgram - платформа для обмена рецептами друг с другом.

### Описание проекта:
#### Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


### Стек применяемых технологий:

- __Python__, 
- __Django__,
- __Django rest framework__, 
- __PostgreSQL__,
- __Docker__,
- __Gunicorn__,
- __Nginx__,
- __GitHub Actions__


### _Запуск проекта на локальном сервере:_ 

1. Клонировать репозиторий:

```
    git clone https://git@github.com:MaksimGolovkin/foodgram.git

```

2. Создайте и активируйте виртуально окружение:
```
    python3 -m venv env
    source env/bin/activate - для Mac/Linux
    source venv/Scripts/activate - для Windows
```

3. Установите зависимости:
```
    pip install -r requirements.txt
```

4. Перейдите в директорию "infra":
```
    cd infra
```

5. Создайте файл с переменными окружения (.env), в которо должны находится слудющие данные:
```
    SECRET_KEY='django-insecure-zbfwqequ&@*&&e%q3b(s5ei=ybhr55rcg@n(qe#f!7dv99y*ip' | (Секретный ключ приложения)
    DEBUG_VALUE=True                                                                | (Переменная включающая/отключающая отладку приложения)
    ALLOWED_HOSTS='51.250.98.98,127.0.0.1,localhost,foodgramishe.hopto.org'         | (Адреса приложения)
    SQLITE3_VALUE='False'                                                           | (Переменная включающая/отключающая использование разных БД в приложение)

    POSTGRES_DB=foodgram_db                                                         | (Переменная наименования БД приложения)
    POSTGRES_USER=foodgram_user                                                     | (Переменная наименования профиля БД приложения)
    POSTGRES_PASSWORD=foodgrampassword                                              | (Пароль от БД приложения)

    DB_NAME=foodgram                                                                | (Имя приложения)
    DB_HOST=db                                                                      | (Имя хоста БД приложения)
    DB_PORT=5432                                                                    | (Порт БД приложения)
```

6. Выолните команду для достпуа к документации:
```
    docker compose up
```

7. Выполните миграции:
```
    cd ..
    cd backend
    python manage.py migrate
```

8. Заполните базу данных некоторыми тестовыми данными ингредиентов:
```
    python manage.py import_data
```

9. Запустить локальный сервер:
```
    python manage.py runserver
```
#### _Для локальной развертки более ничего не требуется, перейдите по адресу_
__

### _Запуск проекта на удаленном сервере:_ 

1. Клонировать репозиторий:

```
    git clone https://git@github.com:MaksimGolovkin/foodgram.git
```

2. Создать Docker-образ для контейнеров:
```
    cd infra
    docker build -t USERNAME/foodgram
```
Вместо USERNAME вставить свой логин на DockerHub.

3. Запушить образы на DockerHub

```
    docker push USERNAME/foodgram
```
Вместо USERNAME вставить свой логин на DockerHub.

4. Подключитесь к удаленному серверу:
```
    ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME YOUR_USERNAME@SERVER_IP_ADDRESS 
```

5. Создайте директорию в которой будет распологаться инструкции для Docker-a:
```
    mkdir foodgram
```

6. Установите Docker Compose на сервер:
```
    sudo apt update
    sudo apt install curl
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo apt install docker-compose
```

7. Скопируйте файлы "docker-compose.production.yml" и ".env" в директорию foodgram/ на сервере:
```
    scp -i PATH_TO_SSH_KEY/SSH_KEY_NAME docker-compose.production.yml YOUR_USERNAME@SERVER_IP_ADDRESS:/home/YOUR_USERNAME/foodgram/docker-compose.production.yml
```
        - 'PATH_TO_SSH_KEY' - путь к файлу с вашим SSH-ключом
        - 'SSH_KEY_NAME' - имя файла с вашим SSH-ключом
        - 'YOUR_USERNAME' - ваше имя пользователя на сервере
        - 'SERVER_IP_ADDRESS' - IP-адрес вашего сервера

```
    scp -i PATH_TO_SSH_KEY/SSH_KEY_NAME docker-compose.production.yml YOUR_USERNAME@SERVER_IP_ADDRESS:/home/YOUR_USERNAME/foodgram/.env
```
        - 'PATH_TO_SSH_KEY' - путь к файлу с вашим SSH-ключом
        - 'SSH_KEY_NAME' - имя файла с вашим SSH-ключом
        - 'YOUR_USERNAME' - ваше имя пользователя на сервере
        - 'SERVER_IP_ADDRESS' - IP-адрес вашего сервера

В файле ".env" необходимо указать переменные окружения, ожидаются следующие:

        - 'SECRET_KEY' - Секректный ключ от Django, установлен по умолчанию.
        - 'DEBUG_VALUE' - Переключатель режима откладки, по умолчанию 'False'
        - 'ALLOWED_HOSTS' - Список строк, представляющих имена хоста/домена, которые может обслуживать Django, по умолчанию 'localhost'
        - 'SQLITE3_VALUE' - Переключатель базы данных, по умолчанию 'False'.
        - 'POSTGRES_DB' - Имя базы данных PostgreSQL.
        - 'POSTGRES_USER' - Имя пользователя PostgreSQL.
        - 'POSTGRES_PASSWORD' - Пароль пользователя PostgreSQL.
        - 'DB_NAME' - адрес, по которому Django будет соединяться с базой данных. (Имя контейнера)
        - 'DB_PORT' - порт, по которому Django будет обращаться к базе данных. 5432 — это порт по умолчанию для PostgreSQL.


8. Запустите контейнеры, перейдя в корневую директорию, командой:
```
    sudo docker compose -f docker-compose.production.yml up -d
```
9. Примените миграции, соберите статику бэкенда и скопируйте для раздачи:
```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
10. Откройте конфигурационный файл Nginx в редакторе nano:
```
    sudo nano /etc/nginx/sites-enabled/default
```

11. Добавьте настройки "location" в секции "server":
```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
```
12. Перезапустите Nginx:
```
    sudo service nginx reload
```

#### _Для удаленной развертки более ничего не требуется_

---
_Автор проекта - maksimgolovkin96. :)_