from ninja import Schema
from typing import Dict


class PollOut(Schema):
    id: int
    question: str


class CreatePoll(Schema):
    question: str
    text: Dict[str, str]


class CreatePollOut(CreatePoll):
    id: int


class ErrorSchema(Schema):
    error: str
