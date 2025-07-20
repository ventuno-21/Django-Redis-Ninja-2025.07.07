VOTE_COOKIE_NAME = "poll_voter"
VOTE_EXPIRE_TIME = 30 * 24 * 60 * 60  # 30 Days


def has_cookie_voted(request, poll_id: int) -> bool:
    voted_polls = request.COOKIES.get(VOTE_COOKIE_NAME, "")

    return str(poll_id) in voted_polls.split(".")


def set_vote_cookie(response, request, pol_id: int):
    # 🔍 Step 1: Retrieve existing vote cookie from the request
    existing = request.COOKIES.get(VOTE_COOKIE_NAME, "")

    #  Step 2: Parse existing cookie value into a set of voted poll IDs
    # If cookie exists, split by commas and convert to set to eliminate duplicates
    voted_polls = set(existing.split(",")) if existing else set()

    # Step 3: Add current poll ID to the set (as string for consistency)
    voted_polls.add(str(pol_id))

    # Step 4: Set the updated cookie on the response
    # Serialize set back into comma-separated string and apply expiration
    response.set_cookie(
        VOTE_COOKIE_NAME,  # Name of the cookie
        ",".join(voted_polls),  # Updated value with new poll ID added
        max_age=VOTE_EXPIRE_TIME,  # Cookie lifespan in seconds
    )
