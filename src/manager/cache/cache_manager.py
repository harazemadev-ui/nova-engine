import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# ENVIRONMENT
# ==========================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
).lower()


# ==========================================
# DATABASE API URL
# ==========================================

def get_redis_url() -> str:

    if ENVIRONMENT == "production":
        url = os.getenv("GLOBAL_REDIS_URL")

    elif ENVIRONMENT == "development":
        url = os.getenv("LOCAL_REDIS_URL")

    else:
        raise RuntimeError(
            f"Invalid ENVIRONMENT: {ENVIRONMENT}. "
            "Use 'development' or 'production'."
        )

    if url is None:
        raise RuntimeError(
            f"Redis API URL is not configured for "
            f"environment: {ENVIRONMENT}"
        )

    return url


REDIS_URL = get_redis_url()


class NovaCacheManager:

    def __init__(self):
        self.client = redis.from_url(
            REDIS_URL,
            db=0,
            decode_responses=True
        )

    # ==========================================
    # GET
    # ==========================================

    def get(
        self,
        cache_key
    ):

        cache = self.client.get(cache_key)

        if cache is None:
            return None

        return json.loads(cache)

    # ==========================================
    # SET
    # ==========================================

    def set(
        self,
        cache_key,
        cache_value,
        expiration=60
    ):

        cache_data = json.dumps(cache_value)

        self.client.set(
            cache_key,
            cache_data,
            ex=expiration
        )

    # ==========================================
    # DELETE
    # ==========================================

    def delete(
        self,
        cache_key
    ):

        self.client.delete(cache_key)
