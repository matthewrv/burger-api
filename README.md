# Burger API

Бекенд для веб-приложения [Stellar Burgers](https://github.com/matthewrv/react-burger).

⚠️ Work In Progress

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