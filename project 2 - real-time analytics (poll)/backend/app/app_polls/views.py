from typing import List

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.shortcuts import render
from ninja import Header, Router

from .models import Poll
from .schemas import CreatePoll, CreatePollOut, ErrorSchema, PollOut, VoteSchema
from .services.cookie_services import has_cookie_voted, set_vote_cookie
from .services.ip_services import get_client_ip
from .services.redis_poll_services import (
    try_register_vote,
    record_vote,
    get_poll_vote_count,
)

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


@router.post(
    "/polls/{poll_id}/vote", response={200: dict, 400: ErrorSchema, 404: ErrorSchema}
)
async def vote(
    request,
    poll_id: int,
    data: VoteSchema,
    x_user_id: str = Header(None),
):

    option_id = data.option

    try:
        poll = await Poll.objects.aget(pk=poll_id)
    except Poll.DoesNotExist:
        return 404, {"error": "Poll not found"}

    if not poll.is_active:
        return 400, {"error": "This poll is not active"}

    if poll.expire_at and poll.is_expired():
        return 400, {"error": "This poll has expired"}

    if option_id not in poll.text:
        return 400, {"error": "Invalid option ID"}

    ip = get_client_ip(request)
    user_id = request.headers.get("X-USER-ID")

    if user_id:
        success = await try_register_vote(poll_id, user_id, "voted_user")
        if not success:
            return 400, {"error": "User has already voted"}

        # if await has_user_voted(poll_id, user_id):
        #     return 400, {"error": "User has laready voted"}
        # await register_user_vote(poll_id, user_id)

    ip_already_voted = not await try_register_vote(poll_id, ip, "voted_ips")

    if ip_already_voted or has_cookie_voted(request, poll_id):
        return 400, {"error": "This ip/browser has already voted"}

    # await increment_vote(poll_id, option_id)
    # await track_recent_vote(poll_id, user_id or "anonymous", ip, option_id)

    await record_vote(poll_id, user_id or "anonymous", ip, option_id)

    response = JsonResponse({"message": f"Vote for option {option_id} is considered"})
    set_vote_cookie(response, request, poll_id)
    return response


@router.get(
    "/polls/{poll_id}/result", response={200: dict, 400: ErrorSchema, 404: ErrorSchema}
)
async def pool_results(request, poll_id: int):
    try:
        poll = await Poll.objects.aget(pk=poll_id)
    except Poll.DoesNotExist:
        return {"error": "requested poll is not found"}

    results = await get_poll_vote_count(poll_id)

    for option_id in poll.text.keys():
        if option_id not in results:
            """
            Ensures every poll option has a vote count, even if it's zero:
            {"1": 12,"2": 8, "3": 0,"4": 0}
            """
            results[option_id] = 0

    total_votes = sum(results.values())

    return {
        "poll_id": poll.id,
        "question": poll.question,
        "options": [{"id": k, "text": v} for k, v in poll.text.items()],
        "results": results,
        "total_votes": total_votes,
    }
