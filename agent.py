import sys
from dataclasses import dataclass

from gigachat import GigaChat, Chat, Messages, MessagesRole
from gigachat.models import JsonSchemaResponseFormat
from pydantic import BaseModel, ValidationError

from schemas import Facts, Application
from prompts import EXTRACT_FACTS, WRITE_APPLICATION, REVIEW_APPLICATION, INVALID_JSON

class AgentError(Exception):
    pass

@dataclass
class Agent:
    client: GigaChat
    idea: str

    async def chat(self, chat: Chat) -> Messages:
        for msg in chat.messages:
            print(">>>", msg.role)
            print(msg.content)

        response = await self.client.achat(chat)
        msg = response.choices[0].message

        print("<<<", msg.role)
        print(msg.content)

        return msg

    async def chat_parse[T: BaseModel](self, chat: Chat, model: type[T], max_retries: int = 2) -> T:
        chat = chat.model_copy(deep=True)
        chat.response_format = JsonSchemaResponseFormat(schema=model.model_json_schema(), strict=True)
        max_retries = max(max_retries, 0)

        while True:
            message = await self.chat(chat)
            try:
                return model.model_validate_json(message.content, strict=False, extra="ignore")
            except ValidationError as err:
                print(err, file=sys.stderr)
                if not max_retries:
                    raise AgentError("Модель не смогла вернуть валидный JSON") from err

                max_retries -= 1
                chat.messages.extend([
                    message,
                    Messages(role=MessagesRole.USER, content=INVALID_JSON),
                    Messages(role=MessagesRole.USER, content=f"Ошибка:\n{err}"),
                ])

    async def extract_facts(self) -> Facts:
        chat = Chat(messages=[
            Messages(role=MessagesRole.SYSTEM, content=EXTRACT_FACTS),
            Messages(role=MessagesRole.USER, content=f"Исходное описание проекта:\n{self.idea}"),
        ])
        return await self.chat_parse(chat, Facts)

    async def write_application(self, facts: Facts) -> Application:
        chat = Chat(messages=[
            Messages(role=MessagesRole.SYSTEM, content=WRITE_APPLICATION),
            Messages(role=MessagesRole.USER, content=f"Исходное описание:\n{self.idea}"),
            Messages(role=MessagesRole.USER, content=f"Извлеченные факты:\n{facts.model_dump_json(indent=2)}"),
        ])
        return await self.chat_parse(chat, Application)

    async def review_application(self, draft: Application) -> Application:
        chat = Chat(messages=[
            Messages(role=MessagesRole.SYSTEM, content=REVIEW_APPLICATION),
            Messages(role=MessagesRole.USER, content=f"Исходное описание:\n{self.idea}"),
            Messages(role=MessagesRole.USER, content=f"Заявка для проверки:\n{draft.model_dump_json(indent=2)}"),
        ])
        return await self.chat_parse(chat, Application)

    async def generate_application(self) -> Application:
        facts = await self.extract_facts()
        draft = await self.write_application(facts)
        application = await self.review_application(draft)
        return application
