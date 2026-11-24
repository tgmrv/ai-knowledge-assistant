from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.schemas import AnswerSchema, QuestionSchema
from app.core.config import Settings
from app.core.dependencies import build_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = build_services(Settings())
    try:
        app.state.rag = services.rag
        yield
    finally:
        await services.close()

app = FastAPI(lifespan=lifespan)

@app.post("/ask", response_model=AnswerSchema)
async def ask(request: Request, payload: QuestionSchema):
    answer = await request.app.state.rag.answer(payload.question)
    return AnswerSchema(answer=answer)