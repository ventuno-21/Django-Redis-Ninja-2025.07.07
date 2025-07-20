from django.conf import settings


r = settings.REDIS_CLIENT


def get_poll_key(poll_id: int, suffix: str):
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
