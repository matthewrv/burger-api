# Burger API

Бекенд для веб-приложения [Stellar Burgers](https://github.com/matthewrv/react-burger).

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

```bash
fastapi dev
```

После этого можно дёргать ручки по адресу http://localhost:8000

### Скрипты

В директории `scripts` есть скрипты для целей тестов и отладки. Пример запуска
скрипта для добавления ингридиентов в базу данных:

```bash
PYTHONPATH=$PWD:$PYTHONPATH python scripts/load_default_ingredients.py
```
