# redis_cart.py
import json

from django.conf import settings

r = settings.REDIS_CLIENT

CART_TTL = 60 * 60  # 30 minutes
# CART_TTL = 60 * 30  # 30 minutes


def _refresh_cart_ttl_pipe(pipe, session_id):
    pipe.expire(_qty_key(session_id), CART_TTL)
    pipe.expire(_details_key(session_id), CART_TTL)
    pipe.expire(f"{_cart_key(session_id)}:promo_code", CART_TTL)


def _cart_key(session_id):
    return f"cart:{session_id}"


def _qty_key(session_id):
    return f"{_cart_key(session_id)}:qty"


def _details_key(session_id):
    return f"{_cart_key(session_id)}:details"


def add_to_cart(session_id, product_id, quantity, name, price):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    pipe = r.pipeline()
    pipe.hincrby(qty_key, product_id, quantity)

    if not r.hexists(details_key, product_id):
        product_data = {
            "product_id": product_id,
            "name": name,
            "price": float(price),
        }
        """
            Redis Hashes Only Store Strings
            Even in hashes (HSET), both keys and values are stored as strings
            Redis won’t understand how to serialize or store that Python dict—it needs a string.
            
            json.dumps(product_data) turns your dictionary into a JSON string so it can be stored cleanly in Redis.
            json.dumps(product_data) converts your Python dict to a structured string.

            This makes your data portable: easy to send over the network, store, and retrieve.
            When you read it back, you can easily turn it into a dictionary again with json.loads().
        """
        pipe.hset(details_key, product_id, json.dumps(product_data))

    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


def get_cart(session_id):
    qtys = r.hgetall(_qty_key(session_id))
    details = r.hgetall(_details_key(session_id))

    cart_items = []

    for pid, qty in qtys.items():
        detail_json = details.get(pid)
        if not detail_json:
            continue

        data = json.loads(detail_json)
        data["quantity"] = int(qty)
        cart_items.append(data)

    return cart_items


def remove_from_cart(session_id, product_id):
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)
    promo_key = f"{_cart_key(session_id)}:promo_code"

    pipe = r.pipeline()
    pipe.hdel(qty_key, product_id)
    pipe.hdel(details_key, product_id)

    if r.hlen(qty_key) == 0:  # 1 left before deletion
        pipe.delete(promo_key)

    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


def clear_cart(session_id):
    pipe = r.pipeline()
    pipe.delete(_qty_key(session_id))
    pipe.delete(_details_key(session_id))
    pipe.delete(f"{_cart_key(session_id)}:promo_code")
    pipe.execute()


def increment_quantity(session_id, product_id, step=1):
    pipe = r.pipeline()
    pipe.hincrby(_qty_key(session_id), product_id, step)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()
    return True


def decrement_quantity(session_id, product_id, step=1):
    """
    What .watch(qty_key) Does
    It monitors the key qty_key for changes by other clients.

    If the key is modified after it's watched (before the transaction with .multi()
    and .execute() is run), Redis will abort the transaction, and raise a WatchError.

    That’s why your code has a try...except r.WatchError block: if something
    else updates qty_key, your code will catch the error and retry (up to 5
    times, as specified by MAX_ATTEMPTS).

    💡 Why It Matters
    This ensures consistency when multiple clients might be updating the
    same shopping cart concurrently.

    Without .watch(), two simultaneous updates could read the same quantity
    and overwrite each other's changes—leading to incorrect final values.

    🧠 Concept Summary
    It's like saying: “Hey Redis, watch this key—if it changes while I’m
    calculating what to do, then cancel everything and let me try again.”
    """
    qty_key = _qty_key(session_id)
    details_key = _details_key(session_id)

    MAX_ATTEMPTS = 5

    for attempt in range(MAX_ATTEMPTS):
        try:
            with r.pipeline() as pipe:
                pipe.watch(qty_key)

                # Use direct client method (not through pipe)
                current_qty = r.hget(qty_key, product_id)
                if current_qty is None:
                    pipe.unwatch()
                    return False

                current_qty = int(current_qty)
                new_qty = current_qty - step

                """
                Role of pipe.multi() and pipe.execute()
                
                pipe.multi():
                This method marks the start of a Redis transaction in the pipeline (pipe).
                It tells Redis to queue all subsequent commands (e.g., pipe.hset, pipe.hdel,
                _refresh_cart_ttl_pipe) without executing them immediately.
                These queued commands are held until pipe.execute() is called, ensuring
                they are executed as a single, atomic unit.
                
                pipe.execute():
                This method sends all the queued commands (from the multi block) to Redis for execution.
                Redis executes these commands atomically, meaning:
                All commands are executed sequentially without interruption by other clients.
                Either all commands succeed or none are applied (e.g., if an error like 
                WatchError occurs).
                If the qty_key being watched (via pipe.watch(qty_key)) was modified by another client
                before execute is called, Redis raises a WatchError, and no commands in the transaction are applied.
                """
                pipe.multi()

                if new_qty < 1:
                    pipe.hdel(qty_key, product_id)
                    pipe.hdel(details_key, product_id)
                else:
                    pipe.hset(qty_key, product_id, new_qty)

                _refresh_cart_ttl_pipe(pipe, session_id)
                pipe.execute()
                return True

        except r.WatchError:
            continue


# def decrement_quantity(session_id, product_id, step=1):
#     qty_key = _qty_key(session_id)
#     details_key = _details_key(session_id)

#     # First, decrement and get new quantity
#     new_qty = r.hincrby(qty_key, product_id, -step)

#     if new_qty < 1:
#         # Quantity too low, clean up
#         pipe = r.pipeline()
#         pipe.hdel(qty_key, product_id)
#         pipe.hdel(details_key, product_id)
#         _refresh_cart_ttl_pipe(pipe, session_id)
#         pipe.execute()
#     else:
#         # Just refresh TTL
#         pipe = r.pipeline()
#         _refresh_cart_ttl_pipe(session_id)
#         pipe.execute()

#     return True


def set_quantity(session_id, product_id, quantity):
    key = _cart_key(session_id)
    existing = r.hget(key, product_id)

    if not existing:
        return False  # Nothing to update

    data = json.loads(existing)
    data["quantity"] = quantity
    r.hset(key, product_id, json.dumps(data))

    pipe = r.pipeline()
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()

    return True


def set_cart_promo_code(session_id, promo_code):
    pipe = r.pipeline()
    pipe.set(f"{_cart_key(session_id)}:promo_code", promo_code)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()


def get_cart_promo_code(session_id):
    key = f"cart:{session_id}:promo_code"
    return r.get(key)


def update_cart_item(session_id, product_id, name, price, quantity):
    pipe = r.pipeline()
    details = {
        "product_id": product_id,
        "name": name,
        "price": float(price),
    }

    pipe.hset(_details_key(session_id), product_id, json.dumps(details))
    pipe.hset(_qty_key(session_id), product_id, quantity)
    _refresh_cart_ttl_pipe(pipe, session_id)
    pipe.execute()
