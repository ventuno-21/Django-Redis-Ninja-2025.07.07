from django.conf import settings


r = settings.REDIS_CLIENT


async def increment_vote(poll_id: int, option_id: str) -> None:
    """Increment the vote counter for an option"""
    key = f"poll:{poll_id}"
    await r.hincrby(key, option_id, 1)
