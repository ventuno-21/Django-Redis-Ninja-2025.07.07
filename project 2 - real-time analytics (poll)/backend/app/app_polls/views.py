from typing import List

from asgiref.sync import sync_to_async
from django.shortcuts import render
from ninja import Router

from .models import Poll
from .schemas import CreatePoll, CreatePollOut, PollOut, ErrorSchema

# Create your views here.

router = Router()


@router.get("/polls", response=List[PollOut])
async def poll_list(request):
    polls = await sync_to_async(list)(Poll.objects.all())
    return polls


@router.post("/polls/add", response={201: CreatePollOut, 400: ErrorSchema})
async def create_poll(request, data: CreatePoll):

    if not data.text or len(data.text) < 2:
        return 400, {"error": "At least two poll options are required"}
    poll = Poll(question=data.question, text=data.text)
    await poll.asave()
    # return 201, CreatePollOut(id=poll.id, question=poll.question, text=poll.text)
    return 201, poll
