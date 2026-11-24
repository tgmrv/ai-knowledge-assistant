import asyncio
from pathlib import Path

from qdrant_client import models

from app.core.config import Settings
from app.core.dependencies import build_services


async def ingest() -> None:
    project_dir = Path(__file__).resolve().parents[1]
    docs_dir = project_dir / "docs" / "microservices_shop"
    files = sorted(docs_dir.rglob("*.md"))
    if not files:
        raise SystemExit("Нет Markdown-файлов для индексации")

    settings = Settings()
    services = build_services(settings)
    collection = settings.COLLECTION

    try:
        for path in files:
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                continue

            source = path.relative_to(project_dir).as_posix()
            await services.rag.index(text, source)

        if not await services.qdrant.collection_exists(collection):
            print("Нет фрагментов для индексации")
            return

        result = await services.qdrant.count(collection, exact=True)
        print(f"{collection}: {result.count} точек")
    finally:
        await services.close()


if __name__ == "__main__":
    asyncio.run(ingest())