# chutils: Рутина — в прошлом!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/chutils.svg)](https://badge.fury.io/py/chutils)

**chutils** — это набор простых утилит для Python, который избавляет от повторяющейся настройки конфигурации,
логирования и секретов в ваших проектах.

Начните новый проект и сразу сфокусируйтесь на главном, а не на рутине.

## Проблема

Каждый раз, начиная новый проект, приходится решать одни и те же задачи:

- Как удобно читать настройки из файла конфигурации?
- Как настроить логирование, чтобы сообщения писались и в консоль, и в файл с ежедневной ротацией?
- Как безопасно хранить API-ключи, не прописывая их в коде?
- Как сделать, чтобы всё это работало "из коробки", без прописывания путей?

**chutils** предлагает готовые решения для всех этих проблем.

## Ключевые возможности

- **✨ Ноль конфигурации:** Библиотека **автоматически** находит корень вашего проекта и файл `config.yml` или
  `config.ini`.
- **⚙️ Гибкая конфигурация:** Поддержка `YAML` и `INI` форматов. Простые функции для получения типизированных данных.
- **✍️ Продвинутый логгер:** Функция `setup_logger()` "из коробки" настраивает логирование в консоль и в ротируемые
  файлы. Возвращает кастомный логгер с дополнительными уровнями отладки (`devdebug`, `mediumdebug`).
- **🔒 Безопасное хранилище секретов:** Модуль `secret_manager` предоставляет простой интерфейс для сохранения и
  получения секретов через системное хранилище ключей (Keyring).
- **🚀 Готовность к работе:** Просто установите и используйте.

## Установка

```bash
poetry add chutils
```

Или с помощью pip:

```bash
pip install chutils
```

Для разработки клонируйте репозиторий и установите его в режиме редактирования:

```bash
git clone https://github.com/Chu4hel/chutils.git
cd chutils
pip install -e .
```

## Примеры использования

В папке [`/examples`](./examples/) вы найдете готовые к запуску скрипты, демонстрирующие ключевые возможности
библиотеки. Каждый пример сфокусирован на одной конкретной задаче.

## Быстрый старт

### 1. Работа с конфигурацией

1. Создайте файл `config.yml` в корне вашего проекта:

   ```yaml
   # config.yml
   Database:
     host: localhost
     port: 5432
     user: my_user
   ```

2. Получайте значения в вашем коде:

   ```python
   # main.py
   from chutils import get_config_value, get_config_int

   db_host = get_config_value("Database", "host", fallback="127.0.0.1")
   db_port = get_config_int("Database", "port", fallback=5433)

   print(f"Подключаемся к БД по адресу: {db_host}:{db_port}")
   # Вывод: Подключаемся к БД по адресу: localhost:5432
   ```
   `chutils` автоматически найдет `config.yml` и прочитает из него данные.

### 2. Настройка логирования

1. Добавьте секцию `Logging` в ваш `config.yml` (опционально):

   ```yaml
   # config.yml
   Logging:
     log_level: DEBUG
     log_file_name: my_app.log
   ```

2. Используйте логгер:

   ```python
   # main.py
   from chutils import setup_logger, ChutilsLogger

   # Настраиваем логгер. Он сам прочитает настройки из конфига.
   logger: ChutilsLogger = setup_logger()

   logger.info("Приложение запущено.")
   logger.debug("Это отладочное сообщение.")
   # Вывод в консоли и запись в файл logs/my_app.log
   ```
   Папка `logs` будет создана автоматически.

### 3. Управление секретами

1. Инициализируйте `SecretManager` и сохраните ваш секрет. **Это нужно сделать один раз.**

   ```python
   # setup_secrets.py
   from chutils import SecretManager

   secrets = SecretManager("my_awesome_app")
   secrets.save_secret("db_password", "MySuperSecretDbPassword123!")
   print("Пароль от БД сохранен в системном хранилище!")
   ```

2. Получайте секрет в основном коде, не "светя" им:

   ```python
   # main.py
   from chutils import SecretManager, get_config_value

   secrets = SecretManager("my_awesome_app")
   db_user = get_config_value("Database", "user")

   # Получаем пароль из безопасного хранилища
   db_password = secrets.get_secret("db_password")

   if db_password:
       print(f"Получен пароль для пользователя {db_user}.")
   else:
       print("Пароль не найден!")
   ```

## Комплексный пример

Этот пример показывает, как все компоненты `chutils` работают вместе.

1. **Файл `config.yml`:**
   ```yaml
   API:
     base_url: https://api.example.com

   Database:
     host: localhost
     port: 5432
     user: my_user

   Logging:
     log_level: INFO
   ```

2. **Код `main.py`:**
   ```python
   # main.py
   from chutils import get_config_value, setup_logger, SecretManager, ChutilsLogger

   # 1. Настраиваем логгер. Он автоматически прочитает настройки из конфига.
   logger: ChutilsLogger = setup_logger()

   # 2. Инициализируем менеджер секретов для нашего приложения.
   secrets = SecretManager("my_awesome_app")

   def setup_credentials():
       """Функция для первоначального сохранения пароля, если его нет."""
       db_user = get_config_value("Database", "user")
       password_key = f"{db_user}_password"

       if not secrets.get_secret(password_key):
           logger.info("Пароль для БД не найден. Сохраняем новый...")
           secrets.save_secret(password_key, "MySuperSecretDbPassword123!")
           logger.info("Пароль для БД сохранен в системном хранилище.")

   def connect_to_db():
       """Пример подключения к БД с использованием конфига и секретов."""
       db_host = get_config_value("Database", "host")
       db_user = get_config_value("Database", "user")
       db_password = secrets.get_secret(f"{db_user}_password")

       if not db_password:
           logger.error("Не удалось получить пароль для БД!")
           return

       logger.info(f"Подключаемся к {db_host} от имени {db_user}...")
       # ... логика подключения ...
       logger.info("Успешно подключились!")

   def main():
       logger.info("Приложение запущено.")
       setup_credentials()
       connect_to_db()
       logger.info("Приложение завершило работу.")

   if __name__ == "__main__":
       main()
   ```

## API

### Работа с конфигурацией (`chutils.config`)

- `get_config_value(section, key, fallback="")`: Получить значение.
- `get_config_int(section, key, fallback=0)`: Получить целое число.
- `get_config_boolean(section, key, fallback=False)`: Получить булево значение.
- `get_config_list(section, key, fallback=[])`: Получить список.
- `get_config_section(section)`: Получить всю секцию как словарь.
- `save_config_value(section, key, value)`: Сохранить значение. Работает для `.yml` и `.ini`.
  **Важно**: при сохранении в `.yml` комментарии и форматирование будут утеряны. При сохранении в `.ini` - сохраняются.

### Настройка логирования (`chutils.logger`)

- `setup_logger(name='app_logger', log_level_str='')`: Настраивает и возвращает экземпляр `ChutilsLogger`.
- `logger.mediumdebug("message")`: Логирование с уровнем 15.
- `logger.devdebug("message")`: Логирование с уровнем 9.

### Управление секретами (`chutils.secret_manager`)

- `SecretManager(service_name)`: Создает менеджер, изолированный по имени сервиса.
- `secrets.save_secret(key, value)`: Сохраняет секрет.
- `secrets.get_secret(key)`: Получает секрет.
- `secrets.delete_secret(key)`: Удаляет секрет.

### Ручная инициализация (`chutils.init`)

В 99% случаев вам это **не понадобится**. Но если автоматика не справилась, вы можете один раз указать путь к проекту
вручную в самом начале работы приложения:

```python
import chutils

chutils.init(base_dir="/path/to/my/project/root")
```

## Лицензия

Проект распространяется под лицензией MIT.
