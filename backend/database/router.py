# backend/database/router.py
import hashlib
import os
import random

SHARD_COUNT = int(os.environ.get("DJANGO_SHARD_COUNT", 3))

def get_shard_id(key: str | int) -> int:
    raw = str(key).encode()
    digest = hashlib.sha256(raw).hexdigest()
    return int(digest, 16) % SHARD_COUNT
