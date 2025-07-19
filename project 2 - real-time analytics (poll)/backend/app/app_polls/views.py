from typing import List

from asgiref.sync import sync_to_async
from django.shortcuts import render
from ninja import Router

from .models import Poll
from .schemas import PollOut

# Create your views here.

router = Router()


@router.get("/polls", response=List[PollOut])
async def poll_list(request):
    polls = await sync_to_async(list)(Poll.objects.all())
    return polls
