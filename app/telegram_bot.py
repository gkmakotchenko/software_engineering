from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from .config import settings
from .summarizer import SummarizationError, SummaryParams, build_summarizer, clamp_text

dp = Dispatcher()
_summarizer = build_summarizer(
    hf_api_token=settings.hf_api_token,
    model_id=settings.hf_model_id,
    timeout_s=settings.hf_timeout_s,
)


HELP_TEXT = (
    "Пришлите текст одним сообщением — я верну краткое резюме.\n\n"
    "Команды:\n"
    "/start — приветствие\n"
    "/help — справка\n"
    "/model — какой моделью пользуемся\n"
)


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer("Привет! Я бот для суммаризации текста.\n\n" + HELP_TEXT)


@dp.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@dp.message(Command("model"))
async def on_model(message: Message) -> None:
    backend = "HF Inference API" if settings.hf_api_token else "local transformers"
    await message.answer(f"Backend: {backend}\nModel: {settings.hf_model_id}")


@dp.message(F.text)
async def on_text(message: Message) -> None:
    text = clamp_text(message.text, settings.max_input_chars)
    if len(text) < 50:
        await message.answer("Текст слишком короткий — пришлите, пожалуйста, хотя бы пару абзацев.")
        return

    await message.chat.do("typing")

    params = SummaryParams(
        max_new_tokens=settings.default_max_new_tokens,
        min_new_tokens=settings.default_min_new_tokens,
    )

    try:
        summary = await asyncio.to_thread(_summarizer.summarize, text, params)
    except SummarizationError as e:
        await message.answer("Не удалось сделать суммаризацию.\n" f"Причина: {e}")
        return
    except Exception as e:  # safety net
        await message.answer(f"Неожиданная ошибка: {type(e).__name__}: {e}")
        return

    if not summary:
        await message.answer("Похоже, модель вернула пустой ответ. Попробуйте другой текст.")
        return

    await message.answer(summary)


async def main() -> None:
    bot = Bot(token=settings.telegram_bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
