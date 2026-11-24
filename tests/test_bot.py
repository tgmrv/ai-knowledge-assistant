from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.bot.main import upload


@pytest.mark.asyncio
async def test_upload_rejects_non_owner(telegram_bot_mock, rag_mock):
    message = SimpleNamespace(
        from_user=SimpleNamespace(id=2),
        document=SimpleNamespace(file_name="orders.md"),
        answer=AsyncMock(),
    )

    await upload(message=message, bot=telegram_bot_mock, rag=rag_mock, owner_id=1)

    message.answer.assert_awaited_once()
    telegram_bot_mock.download.assert_not_called()
    rag_mock.index.assert_not_called()
