# Burger API

Бекенд для веб-приложения [Stellar Burgers](https://github.com/matthewrv/react-burger) - демо-приложение на котором я пробую и обкатываю технологии.

⚠️ Work In Progress

[![Tests](https://github.com/matthewrv/burger-api/actions/workflows/validation.yaml/badge.svg)](https://github.com/matthewrv/burger-api/actions/workflows/validation.yaml)
![FastAPI](https://img.shields.io/badge/FastAPI-262626?logo=fastapi&logoColor=white&style=flat)
![Pydantic](https://img.shields.io/badge/Pydantic-262626?logo=pydantic&logoColor=white&style=flat)
![PyJWT](https://img.shields.io/badge/pyjwt-262626?logo=jsonwebtokens&logoColor=white&style=flat)
![SQLModel](https://img.shields.io/badge/SQLModel-262626?logo=sqlite&logoColor=white&style=flat)
![Alembic](https://img.shields.io/badge/alembic-262626?logo=alembic&logoColor=white&style=flat)
![WebSockets](https://img.shields.io/badge/websockets-262626?logo=websocket&logoColor=white&style=flat)
![Pytest](https://img.shields.io/badge/PyTest-262626?logo=pytest&logoColor=white&style=flat)
![aio_pika](https://img.shields.io/badge/Rabbitmq/aio_pika-262626?style=flat&logo=rabbitmq&logoColor=white)

Кроме собственно кода проекта рекомендую заглянуть в доки - например, [сюда](https://github.com/matthewrv/burger-api/blob/main/docs/perfomance_improvments.md). Там красивые графики и диаграммы с замерами производительности.

## Разработка

### Начало работы

Если вы используете NixOS (как и я btw), то для настройки окружения достаточно выполнить команду:

```bash
nix-shell
```

Если у вас не NixOS и ещё не установлен `uv`, установите 😼 [Документация](https://docs.astral.sh/uv/#installation)

После чего выполните команду

```
uv sync
```

Управление зависимостями в проекте ведётся через `uv`.

### Локальный запуск

Перед первым запуском создайте `.env` файл с помощью команды:

```bash
./pleh.sh init-dotenv
```

Затем, запустите приложение со всем окружением через docker compose

```bash
docker compose up --build -d
```

Приложение запустится в контейнере burger-api с примонтировнными директориями app и scripts и включенным hot-reload. После этого можно дёргать ручки по адресу http://localhost:8000 или через интерфейс swagger по адресу http://localhost:8000/docs.

Если запускаете в первый раз, рекомендуется прогнать скрипт для заполнения базы данных:

```bash
docker container exec burger-api ./pleh.sh script scripts/load_default_ingredients.py
```

#### Альтернативный вариант

Если хочется запустить приложение на хосте, а не в контейнере (например, для удобства отладки), можно сделать так:

0. Подправить .env файл заменив в нём доменные имена rabbitmq и базы данных на localhost
1. Поднять окружение и приложение по предыдущей инструкции
2. Остановить контейнер burger-api `docker container stop burger-api`
3. Запустить приложение с помощью команды `python main.py`

### Pleh.sh

В репозитории содержится bash скрипт со всякими полезностями.

Примеры использования:

```bash
# Документация по использованию скрипта
./pleh.sh

# Запуск скриптов из директории scripts
./pleh.sh script scripts/load_default_ingredients.py

# Запуск тестов
./pleh.sh test
# Можно добавить аргументов для pytest
./pleh.sh test -vv -k 'ingredient'

# Форматирование кода
./pleh.sh format
```
