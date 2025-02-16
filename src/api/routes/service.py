"""
    This route is responsible for handling the similarity or neural network model logic.
    It receives a POST request with a JSON payload containing the entity input and API Key.
    The route then:
        1. Validates the JWT from the Authorization header.
        2. Validates the API Key in PostgreSQL.
        3. Rate-limits the request via Redis.
        4. Performs ML inference with the TransHModel.
        5. Returns the result, cached in Redis if needed.
        
    If the JWT is invalid, the route returns a 401 Unauthorized error.
    If the API Key is invalid, the route returns a 401 Unauthorized error.
    If the API Key is not provided, the route returns a 401 Unauthorized error.
    If the JWT is expired, the route returns a 401 Unauthorized error.
        
"""

import json
import time
import os
import jwt

from fastapi import APIRouter, Request, HTTPException, status
from src.api.schemas import SimilarityRequest, SimilarityResponse
from src.core.database import get_api_key_info
from src.core.redis_client import get_redis_client, get_cached_results, set_cached_results
from src.utils.logger import init_logger

logger = init_logger(debug=True)
router = APIRouter()


# ----------------------------------------------------------
# Rate Limit Configuration
# ----------------------------------------------------------
RATE_LIMITS = {
    "FREEMIUM": 5,    # 5 requests per minute
    "PREMIUM": 50     # 50 requests per minute
}


@router.post("/service", response_model=SimilarityResponse)
async def similarity_service(request: Request, req_data: SimilarityRequest):
    """
    Handles the similarity or neural network model logic.
    Steps:
      1. Validate JWT from Authorization header.
      2. Validate the API Key in PostgreSQL.
      3. Rate-limit via Redis.
      4. Perform ML inference with TransHModel.
      5. Return the result, cached in Redis if needed.
    """
    # Validate JWT
    token_header = request.headers.get("Authorization")
    if not token_header or not token_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT Token not provided."
        )
    token = token_header.split(" ")[1]
    try:
        jwt.decode(token, os.getenv(
            "SECRET_KEY"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT Token has expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT Token."
        )

    # Validate API Key
    api_key = req_data.api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key not provided."
        )
    database_info = get_api_key_info(api_key)
    if not database_info or database_info.get("api_key") != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key."
        )

    # Rate Limit
    account_type = database_info.get("account_type", "FREEMIUM")
    _check_rate_limit(api_key, account_type)

    # Check Redis Cache

    cached_response = get_cached_results(req_data.entity_input)

    if cached_response:
        logger.info(f"Cache hit for entity {req_data.entity_input}")
        return SimilarityResponse(**cached_response)

    logger.info(f"Cache miss for entity {req_data.entity_input}")

    # Perform ML inference
    transh_model = request.app.state.transh_model
    probability = transh_model.predict_similarity(req_data.entity_input)

    # Store in cache
    set_cached_results(req_data.entity_input, probability)

    # Return the result
    return SimilarityResponse(
        cache=False,
        result=probability
    )


# ------------------------------
# Private helper functions
# ------------------------------

def _check_rate_limit(api_key: str, account_type: str) -> None:
    """
    Uses Redis to track how many requests an API key has made in the current minute.
    Raises 429 Too Many Requests if the usage exceeds the allowed limit for the account type.

    :param r_client: The Redis client instance.
    :param api_key: The user's API key to check usage against.
    :param account_type: User's plan type ("FREEMIUM" or "PREMIUM").
    :raises HTTPException: If the rate limit is exceeded, returns a 429 status.
    """
    logger.info(f"Checking rate limit for API key {api_key}")
    current_minute = int(time.time() // 60)
    redis_key = f"usage:{api_key}:{current_minute}"
    logger.debug(f"Redis key: {redis_key}")

    # Increment usage counter in Redis
    usage_count = get_redis_client().incr(redis_key)

    # Set a 60-second expiry if this is the first request in the current minute
    if usage_count == 1:
        get_redis_client().expire(redis_key, 60)

    # Determine the limit based on account type
    limit = RATE_LIMITS.get(account_type, RATE_LIMITS["FREEMIUM"])
    if usage_count > limit:
        logger.warning(f"Rate limit exceeded for API key {api_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
