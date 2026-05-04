#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Architecture:
  - Horizontal data sharding across N shard databases (shard_0..shard_N)
  - Each shard has an async read replica (shard_0_replica..shard_N_replica)
  - ShardRouter directs writes to primaries, reads to replicas
  - SHARD_COUNT controls the number of shards; no other change needed to scale
"""

import hashlib
import os
import random
import sys


# ── Sharding configuration ────────────────────────────────────────────────────

SHARD_COUNT = int(os.environ.get("DJANGO_SHARD_COUNT", 3))


def get_shard_id(key: str | int) -> int:
    """Return a stable shard index for any hashable partition key."""
    raw = str(key).encode()
    digest = hashlib.sha256(raw).hexdigest()
    return int(digest, 16) % SHARD_COUNT


def build_databases(base: dict) -> dict:
    """
    Expand a single 'default' database config into shard primary + replica pairs.

    base = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "mydb",
            "HOST": "primary-0.example.com",
            ...
        }
    }

    Returns a DATABASES dict with:
      default, shard_0, shard_0_replica, shard_1, shard_1_replica, ...
    """
    databases = {"default": base["default"]}

    for shard_id in range(SHARD_COUNT):
        primary_host = os.environ.get(
            f"DB_SHARD_{shard_id}_HOST",
            f"primary-{shard_id}.db.example.com",
        )
        replica_host = os.environ.get(
            f"DB_SHARD_{shard_id}_REPLICA_HOST",
            f"replica-{shard_id}.db.example.com",
        )

        shard_base = {
            **base["default"],
            "HOST": primary_host,
            "NAME": os.environ.get(f"DB_SHARD_{shard_id}_NAME", f"shard_{shard_id}"),
        }

        databases[f"shard_{shard_id}"] = shard_base
        databases[f"shard_{shard_id}_replica"] = {
            **shard_base,
            "HOST": replica_host,
            "TEST": {"MIRROR": f"shard_{shard_id}"},  # mirrors primary during tests
        }

    return databases


# ── Shard router ──────────────────────────────────────────────────────────────

class ShardRouter:
    """
    Routes database operations across shard primaries and their read replicas.

    Usage in settings.py:
        DATABASE_ROUTERS = ["manage.ShardRouter"]
        DATABASES = build_databases({"default": {...}})
    """

    REPLICA_READ_PROBABILITY = float(
        os.environ.get("REPLICA_READ_PROBABILITY", 0.8)
    )

    # Models whose writes must always go to the default DB (e.g. Django internals)
    DEFAULT_ONLY_APPS = frozenset(
        os.environ.get("DEFAULT_ONLY_APPS", "contenttypes,auth,sessions,admin").split(",")
    )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _shard_alias(shard_id: int, *, replica: bool = False) -> str:
        suffix = "_replica" if replica else ""
        return f"shard_{shard_id}{suffix}"

    def _route(self, app_label: str, *, replica: bool = False) -> str | None:
        if app_label in self.DEFAULT_ONLY_APPS:
            return None  # let Django pick 'default'

        # Without an explicit partition key we round-robin across shards.
        shard_id = random.randrange(SHARD_COUNT)
        return self._shard_alias(shard_id, replica=replica)

    # ── Django router interface ───────────────────────────────────────────────

    def db_for_read(self, model, **hints):
        """
        Direct reads to a replica with REPLICA_READ_PROBABILITY probability.
        Pass hints["shard_key"] to pin a query to a specific shard.
        """
        shard_key = hints.get("shard_key")
        use_replica = random.random() < self.REPLICA_READ_PROBABILITY

        if shard_key is not None:
            shard_id = get_shard_id(shard_key)
            return self._shard_alias(shard_id, replica=use_replica)

        return self._route(model._meta.app_label, replica=use_replica)

    def db_for_write(self, model, **hints):
        """Always write to a shard primary."""
        shard_key = hints.get("shard_key")

        if shard_key is not None:
            shard_id = get_shard_id(shard_key)
            return self._shard_alias(shard_id, replica=False)

        return self._route(model._meta.app_label, replica=False)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations only within the same shard (or the default db)."""
        db_set = {obj1._state.db, obj2._state.db}
        # Both on default: fine
        if db_set <= {"default"}:
            return True
        # Both on the same shard (primary ↔ replica is OK): fine
        shard_ids = {db.replace("_replica", "") for db in db_set}
        return len(shard_ids) == 1

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Run migrations on every primary shard (not on replicas — they mirror).
        Default-only apps migrate only on 'default'.
        """
        if db.endswith("_replica"):
            return False
        if app_label in self.DEFAULT_ONLY_APPS:
            return db == "default"
        return db.startswith("shard_")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simple.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
