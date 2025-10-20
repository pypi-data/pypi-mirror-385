from enum import StrEnum
from pydantic import BaseModel, ConfigDict
from fastapi.requests import Request


class MessageCategory(StrEnum):
    PRIMARY = "primary"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class Message(BaseModel):
    text: str
    category: MessageCategory

    model_config = ConfigDict(frozen=True)


def flash_message(request: Request, message: Message) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(message.model_dump_json())


def get_flashed_messages(request: Request):
    return (
        [Message.model_validate_json(m) for m in request.session.pop("_messages")]
        if "_messages" in request.session
        else []
    )
