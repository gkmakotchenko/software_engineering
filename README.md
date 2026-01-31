# Telegram бот для суммаризации текста

Проект соответствует требованиям итогового проекта: есть **API-приложение (FastAPI)** + **Telegram-бот**, код в GitHub, CI (тесты + PEP8/линтинг), работа через ветки и code review. fileciteturn0file0

## 1) Что делает

- Telegram-бот принимает текст и возвращает краткое резюме.
- API: `POST /summarize` — получить суммаризацию по HTTP.

Суммаризация делается **готовой предобученной моделью** с Hugging Face:
- по умолчанию через **Hugging Face Inference API** (серверless, модель не хостите сами) citeturn0search6turn0search0  
- модель по умолчанию: `cointegrated/rut5-base-absum` (русская абстрактивная суммаризация) citeturn0search2

> Если хотите — можно переключиться на локальный запуск модели (см. ниже), но для облака обычно проще HF Inference API.

---

## 2) Локальный запуск (macOS / Linux / Windows)

### 2.1 Установка

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2.2 Настройка переменных окружения

Создайте файл `.env` в корне:

```env
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
HF_API_TOKEN=hf_xxx   # рекомендовано (иначе будет пытаться запускать локальную модель)
HF_MODEL_ID=cointegrated/rut5-base-absum
```

- `HF_API_TOKEN` — токен Hugging Face (Settings → Access Tokens). Для запросов нужен Bearer-токен. citeturn0search0

### 2.3 Запуск бота

```bash
python -m app.telegram_bot
```

### 2.4 Запуск API

```bash
uvicorn app.api:app --reload --port 8000
```

Проверка:
- `GET http://127.0.0.1:8000/health`
- `POST http://127.0.0.1:8000/summarize` с JSON `{"text":"..."}`

---

## 3) Тесты и линтер

```bash
ruff check .
ruff format .
pytest -q
```

---

## 4) GitHub: как правильно вести разработку (ветки + PR + code review)

Рекомендуемый flow:
1. `main` — стабильная ветка (релизы/защита).
2. `develop` — интеграционная ветка.
3. Фича делается в ветке `feature/<name>`.

Пример:

```bash
git checkout -b develop
git push -u origin develop

git checkout -b feature/telegram-commands
# ... changes
git add .
git commit -m "Add /help and /model commands"
git push -u origin feature/telegram-commands
```

Далее:
- создаёте Pull Request в `develop`
- коллега делает review
- CI должен быть зелёным (tests + ruff)
- merge

---

## 5) CI (GitHub Actions)

Workflow находится в `.github/workflows/ci.yml` и запускается на `push` и `pull_request`:
- `ruff check` + `ruff format --check`
- `pytest` fileciteturn0file0

---

## 6) Деплой: нужно ли на Hugging Face?

По заданию нужно развернуть приложение в облаке (подойдут Streamlit Cloud / Яндекс.Облако / Hugging Face Spaces). fileciteturn0file0  
**Деплоить именно на Hugging Face не обязательно**, достаточно выбрать *одну* платформу.

Но нюанс:
- Telegram-бот — это **долгоживущий процесс**. На платформах типа Spaces/Streamlit Cloud он может «засыпать», если нет трафика.
- Поэтому самый практичный вариант:  
  **API** можно разместить где угодно (в том числе HF Spaces), а **бот** — на VPS/облаке (например, VM в Яндекс.Облаке) и он будет стабильно онлайн.

### Вариант A (самый простой и надёжный): Яндекс.Облако VM + Docker
1. Поднимите VM (Ubuntu).
2. Установите Docker.
3. Склонируйте репозиторий.
4. Запустите API контейнером и бота отдельным процессом (или вторым контейнером).

API:
```bash
docker build -t summarizer-api .
docker run -d --name summarizer-api -p 8000:8000 --env-file .env summarizer-api
```

Бот (на VM без Docker):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.telegram_bot
```

### Вариант B: Hugging Face Spaces (Docker Space) — только API/демо
Если хотите «красивую ссылку» на облачное демо:
- создайте **Space → Docker**
- добавьте туда этот репозиторий
- Space запустит `Dockerfile` (по умолчанию — FastAPI)

⚠️ Для постоянной работы Telegram-бота Spaces может быть нестабилен из-за сна — поэтому лучше бот держать на VM.

---

## 7) Про модель и обучение

Обучать модель не нужно — можно использовать готовую с Hugging Face. fileciteturn0file0  
В проекте уже заложен вариант через HF Inference API (готовая модель + удалённый инференс). citeturn0search6turn0search2

---

## 8) Командная часть (что показать на защите)

За 10 минут обычно хватает:
- показать PR'ы + code review
- показать, что CI зелёный
- показать бота в Telegram (пара примеров)
- показать деплой (URL API или VM) и health-check
