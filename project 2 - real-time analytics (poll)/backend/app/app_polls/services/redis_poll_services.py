from django.conf import settings
import json

r = settings.REDIS_CLIENT


def get_poll_key(poll_id: int, suffix: str) -> str:
    return f"poll:{poll_id}:{suffix}"


async def increment_vote(poll_id: int, option_id: str) -> None:
    """Increment the vote counter for an option"""
    key = get_poll_key(poll_id, "votes")
    # key = f"poll:{poll_id}"
    await r.hincrby(key, option_id, 1)


async def try_register_vote(poll_id: int, voter_id: str, suffix: str) -> bool:
    """
    instead of using two functions with name register_user_vote &
    has_user_voted, we can using only one function

    Attempts to register an user vote,
    returns True if successful and False if user has already voted
    """
    # key = get_poll_key(poll_id, "voted_users")
    key = get_poll_key(poll_id, suffix)
    added = await r.sadd(key, voter_id)
    return added == 1  # 1 => added , 0 => alredy exists


# # register_user_vote and has_user_voted functions are replaced by try_register_vote
# async def register_user_vote(poll_id: int, user_id: str) -> None:
#     """Register a user as having voted"""
#     key = get_poll_key(poll_id, "voted_users")
#     await r.sadd(key, user_id)


# # register_user_vote and has_user_voted functions are replaced by try_register_vote
# async def has_user_voted(poll_id: int, user_id: str) -> bool:
#     """Register a user as having voted"""
#     key = get_poll_key(poll_id, "voted_users")
#     return await r.sismember(key, user_id)


async def record_vote(poll_id: int, voter_id: str, ip: str, option_id: str):
    vote_key = get_poll_key(poll_id, "votes")
    recent_key = get_poll_key(poll_id, "recent_votes")

    vote_data = {"user_id": voter_id, "ip": ip, "option_id": option_id}

    async with r.pipeline(transaction=True) as pipe:
        pipe.hincrby(vote_key, option_id, 1)
        pipe.lpush(recent_key, json.dumps(vote_data))
        pipe.ltrim(recent_key, 0, 99)
        await pipe.execute()


# # track_recent_vote & get_recent_vote functions are replaced with record_vote
# async def track_recent_vote(poll_id: int, user_id: str, ip: str, option_id: str):
#     key = get_poll_key(poll_id, "recent_votes")
#     vote_data = {"user_id": user_id, "ip": ip, "option_id": option_id}

#     await r.lpush(key, json.dumps(vote_data))
#     await r.ltrim(key, 0, 99)  # only last 100 entries will be kept


# # track_recent_vote & get_recent_vote functions are replaced with record_vote
# async def get_recent_vote(poll_id: int) -> list:
#     key = get_poll_key(poll_id, "recent_votes")
#     votes = await r.lrange(key, 0, 99)  # only last 100 entries
#     return [json.loads(v) for v in votes]
