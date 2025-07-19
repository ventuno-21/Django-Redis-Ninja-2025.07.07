from ninja import Schema


class PollOut(Schema):
    id: int
    question: str
