import asyncio
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request, Response, Form, UploadFile, HTTPException
from fastapi.exception_handlers import http_exception_handler
from gigachat import GigaChat, RateLimitError
from dotenv import load_dotenv

from schemas import Application
from agent import Agent, AgentError
from transcriber import Transcriber, TranscriberError

load_dotenv()
transcriber = Transcriber()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict[str, GigaChat]]:
    async with GigaChat(max_retries=2) as client:
        yield {"gigachat": client}

app = FastAPI(lifespan=lifespan)

@app.post("/api/generate")
async def generate(request: Request, idea: Annotated[str, Form()]) -> Application:
    idea = idea.strip()
    if not idea:
        return Application()

    agent = Agent(request.state.gigachat, idea)
    return await agent.generate_application()

@app.post("/api/generate/from_audio")
async def generate_from_audio(request: Request, idea: UploadFile) -> Application:
    buffer = await idea.read()
    text = await asyncio.to_thread(transcriber.transcribe, buffer)
    return await generate(request, text)

@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError) -> Response:
    print(exc, file=sys.stderr)
    err = HTTPException(status_code=502, detail="Не удалось сформировать заявку. Попробуйте перефразировать описание.")
    return await http_exception_handler(request, err)

@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> Response:
    print(exc, file=sys.stderr)
    err = HTTPException(status_code=503, detail="Сервис перегружен. Повторите попытку позже.")
    return await http_exception_handler(request, err)

@app.exception_handler(TranscriberError)
async def transcriber_error_handler(request: Request, exc: TranscriberError) -> Response:
    print(exc, file=sys.stderr)
    err = HTTPException(status_code=400, detail="Не удалось обработать аудиозапись. Используйте текстовый ввод.")
    return await http_exception_handler(request, err)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
