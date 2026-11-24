import asyncio
import json
from pathlib import Path

from app.core.config import Settings
from app.core.dependencies import build_services

CASES_FILE = Path(__file__).with_name("questions.json")
TOP_K = 3


async def main() -> None:
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    if not cases:
        raise SystemExit("В questions.json нет вопросов")

    services = build_services(Settings())
    hits = 0

    try:
        for case in cases:
            question = case["question"]
            expected = case["expected_path"].removeprefix("docs/")
            chunks = (await services.rag.search(question))[:TOP_K]

            paths = [chunk.metadata.source.removeprefix("docs/") for chunk in chunks]
            hit = expected in paths
            hits += int(hit)

            found = ", ".join(paths) or "нет фрагментов"
            status = "OK" if hit else "MISS"
            print(f"{status}  {question}\n    Ожидали {expected}. Поиск: {found}")
    finally:
        await services.close()

    print(f"\nHit@{TOP_K} = {hits}/{len(cases)} ({hits / len(cases):.0%})")


if __name__ == "__main__":
    asyncio.run(main())