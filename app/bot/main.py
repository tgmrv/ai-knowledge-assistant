import asyncio
import logging
from io import BytesIO
from pathlib import PurePath

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.config import Settings
from app.core.dependencies import build_services
from app.rag.service import RAGService


dp = Dispatcher()
dp.message.filter(F.chat.type == ChatType.PRIVATE)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    if message.from_user is not None:
        await message.answer(
            f"Пришли вопрос по документации."
        )


@dp.message(F.document)
async def upload(
    message: Message, bot: Bot, rag: RAGService, owner_id: int | None
) -> None:
    if message.from_user is None or message.from_user.id != owner_id:
        await message.answer("Загружать файлы может только владелец бота.")
        return

    document = message.document
    if document is None or not document.file_name:
        await message.answer("Пришли Markdown-файл с расширением .md.")
        return

    filename = PurePath(document.file_name).name
    if PurePath(filename).suffix.lower() != ".md":
        await message.answer("Пришли Markdown-файл с расширением .md.")
        return

    try:
        with BytesIO() as buffer:
            await bot.download(document, destination=buffer)
            text = buffer.getvalue().decode("utf-8-sig")

        if not text.strip():
            await message.answer("Файл пустой.")
            return

        await rag.index(text, source=f"docs/microservices_shop/{filename}")
    except UnicodeDecodeError:
        await message.answer("Сохрани файл в UTF-8 и отправь его снова.")
        return
    except Exception as exc:
        logging.error("Ошибка загрузки %s (%s)", filename, type(exc).__name__)
        await message.answer("Не удалось добавить файл в поиск.")
        return

    await message.answer(f"Файл {filename} добавлен в поиск.")


@dp.message(F.text)
async def ask(message: Message, rag: RAGService) -> None:
    question = (message.text or "").strip()
    if not question:
        return

    try:
        answer = await rag.answer(question)
    except Exception:
        logging.exception("Ошибка получения ответа RAG")
        await message.answer("Не удалось получить ответ. Попробуй ещё раз.")
        return

    answer = answer.strip() or "Недостаточно данных для ответа"
    for offset in range(0, len(answer), 2000):
        await message.answer(answer[offset:offset + 2000])


async def main() -> None:
    settings = Settings()
    secret = settings.TELEGRAM_BOT_TOKEN
    token = secret.get_secret_value().strip() if secret is not None else ""
    if not token:
        raise SystemExit("Задай TELEGRAM_BOT_TOKEN для запуска бота")

    services = build_services(settings)

    try:
        async with Bot(token=token) as bot:
            await dp.start_polling(
                bot,
                rag=services.rag,
                owner_id=settings.TELEGRAM_OWNER_ID,
                close_bot_session=False,
                handle_as_tasks=False,
            )
    finally:
        await services.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())