# income_expense_bot
## Описание

Телеграм-бот, который позволяет вести статистику доходов и расходов путем заполнения <br>
excel таблицы, находящаяся на яндекс диске.
## Config

Путь к файлу задаётся через `CONFIG_PATH` (по умолчанию `config.json`).

```json
{
  "local_xlsx_path": "./test.xlsx",
  "log_file_path": "/var/log/test.log",
  "year": "2026",
  "ya_xlsx_path": "/test.xlsx",
  "allowed_user_ids": [123456789],
  "default_income": {"id": 20, "name": "job", "min_col": 21, "min_row": 2, "max_col": 24},
  "default_expense": {"id": 4, "name": "delivery cafe", "min_col": 2, "min_row": 2, "max_col": 19}
}
```

`allowed_user_ids` — опционально; если не указано, доступ открыт для всех.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `INCOME_EXPENSE_BOT_TOKEN` | Токен Telegram-бота |
| `KEY` | Fernet-ключ для расшифровки токена Яндекс.Диска |
| `YA_TOKEN_ENCRYPTED` | Зашифрованный OAuth-токен Яндекс.Диска |
| `ALLOWED_USER_IDS` | Telegram user ID через запятую (опционально, если пусто — доступ для всех) |
| `CONFIG_PATH` | Путь к конфигу (опционально) |

## Подготовка токена Яндекс.Диска (один раз, локально)

```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print("Key:", key.decode())  # → KEY

cipher = Fernet(key)
encrypted = cipher.encrypt(b"твой_токен_яндекс_диска")
print("Encrypted:", encrypted.decode())  # → YA_TOKEN_ENCRYPTED
```

## Запуск

```bash
export INCOME_EXPENSE_BOT_TOKEN="токен_бота"
export KEY="fernet_ключ"
export YA_TOKEN_ENCRYPTED="зашифрованная_строка"
source .venv/bin/activate
python income_expense_bot.py
```

## Деплой на сервер

Деплой происходит автоматически при пуше в `main` через GitHub Actions.

### Первоначальная настройка сервера (один раз)

**1. Создать пользователя `github_actions_user` на сервере**

Используй скрипт из [vps_customization](https://github.com/zhuvla/vps_customization).
Сгенерируй SSH-ключ локально:

```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key
```

На сервере:
```bash
sudo bash scripts/setup_user.sh github_actions_user "$(cat ~/.ssh/github_actions_key.pub)"
```

**2. Создать директорию приложения**

```bash
sudo mkdir -p /opt/income_expense_bot
sudo chown github_actions_user:github_actions_user /opt/income_expense_bot
```

**3. Создать `env.env` с секретами**

```bash
nano /opt/income_expense_bot/env.env
```

```
INCOME_EXPENSE_BOT_TOKEN=...
KEY=...
YA_TOKEN_ENCRYPTED=...
CONFIG_PATH=/opt/income_expense_bot/config.json
```

**4. Добавить secrets в GitHub репозиторий**

| Secret | Значение |
|--------|---------|
| `SSH_KEY` | содержимое `~/.ssh/github_actions_key` |
| `SSH_HOST` | IP сервера |
| `SSH_PORT` | SSH порт |
| `SSH_USER` | `github_actions_user` |

После этого любой пуш в `main` автоматически деплоит бота на сервер.

### Прокси (если Telegram заблокирован)

Если сервер находится в регионе с блокировкой Telegram, добавь в `env.env`:

```
HTTPS_PROXY=http://127.0.0.1:7896
ALL_PROXY=http://127.0.0.1:7896
```

`deploy.sh` автоматически подхватит эти переменные и пропишет их в systemd-юнит.
