# Telegram-бот для суммаризации текста

Учебный проект по дисциплине «Программная инженерия».
Реализован Telegram-бот и HTTP API для автоматической суммаризации текста с использованием готовой предобученной нейросетевой модели без её обучения.

Проект соответствует требованиям итогового задания:
- API-приложение (FastAPI)
- Telegram-бот
- Использование готовой ML-модели (без обучения)
- GitHub-репозиторий
- CI (линтер + тесты)
- Работа через ветки и Pull Request

---

## 1. Функциональность

### Telegram-бот
- Принимает текст от пользователя
- Возвращает краткое содержание (summary)

### HTTP API
- POST /summarize — суммаризация текста
- GET /health — проверка работоспособности сервиса

---

## 2. Используемая модель и ИИ-часть

Для суммаризации используется Hugging Face Inference API (serverless inference).

- Модель: facebook/bart-large-cnn
- Тип: encoder-decoder (BART)
- Язык: английский
- Обучение модели не выполняется

Модель вызывается по HTTP через официальный endpoint:

https://router.huggingface.co/hf-inference/models/{model_id}

Таким образом:
- модель не хранится локально
- GPU и собственная ML-инфраструктура не требуются
- используется готовая предобученная модель как сервис

---

## 3. Стек технологий

- Python 3.11
- FastAPI
- aiogram 3
- Hugging Face Inference API
- pytest
- ruff (lint + format)
- GitHub Actions (CI)

---

## 4. Установка и локальный запуск

### 4.1 Клонирование репозитория

git clone https://github.com/<username>/software_engineering.git
cd software_engineering

### 4.2 Виртуальное окружение

python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate    # Windows

### 4.3 Установка зависимостей

pip install -r requirements.txt

---

## 5. Настройка переменных окружения

В корне проекта создайте файл .env:

TELEGRAM_BOT_TOKEN=123456:ABCDEF...
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxx
HF_MODEL_ID=facebook/bart-large-cnn

- TELEGRAM_BOT_TOKEN — токен Telegram-бота (BotFather)
- HF_API_TOKEN — Access Token Hugging Face
- HF_MODEL_ID — используемая модель

---

## 6. Запуск приложения

### 6.1 Запуск Telegram-бота

python -m app.telegram_bot

### 6.2 Запуск API

uvicorn app.api:app --reload --port 8000

### 6.3 Проверка API

Swagger UI:
http://127.0.0.1:8000/docs

Пример запроса:

POST /summarize
{
  "text": "Long English text..."
}

---

## 7. Тесты и линтер

### 7.1 Линтер

ruff check .

### 7.2 Форматирование кода

ruff format .

### 7.3 Тесты

pytest

Рекомендуемый порядок перед коммитом:

ruff format . && ruff check . && pytest

---

## 8. CI (GitHub Actions)

CI настроен в .github/workflows/ci.yml и запускается на push и pull_request.

Выполняется:
- ruff check
- ruff format --check
- pytest

CI гарантирует соблюдение PEP8 и прохождение тестов.

---

## 9. Git-workflow

Используется стандартный flow:
- main — стабильная версия
- develop — ветка разработки
- feature/* — ветки для отдельных задач

Пример:

git checkout -b feature/api
git commit -m "Add summarization API"
git push -u origin feature/api

Далее создаётся Pull Request и выполняется code review.

---

## 10. Деплой

Деплой на Hugging Face не является обязательным.

Telegram-бот является долгоживущим процессом, поэтому наиболее надёжный вариант — запуск на VM или VPS (например, в Яндекс.Облаке).
API может быть размещено там же или отдельно.

---

## 11. Ограничения

- Модель facebook/bart-large-cnn предназначена для английского языка
- Для русского языка потребуется другая модель или локальный запуск

---

## 12. Демонстрация на защите

- GitHub-репозиторий
- История коммитов и Pull Requests
- Успешный CI
- Работа Telegram-бота
- Работа API (/summarize)
