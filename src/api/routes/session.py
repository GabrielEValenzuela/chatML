"""
    This route is responsible for registering new users.
    It receives a POST request with a JSON payload containing the user's email and password. The route then:
        1. Hashes the user's password and stores it in MongoDB.
        2. Generates a new API Key and inserts it into PostgreSQL.
        3. Returns the generated API Key to the user.
    If the user already exists, the route returns a 400 Bad Request error.

    Also allow logging in with an existing user.
    In this scenario, the flow is as follows:
        1. Verify the user's email and password.
        2. Return the user's JWT.
    If the user does not exist or the password is incorrect, the route returns a 400 Bad Request error.
"""

from passlib.context import CryptContext
import jwt
import os
import time

from fastapi import APIRouter, HTTPException, status
from src.api.schemas import RegisterRequest, APIKeyResponse
from src.core.database import create_user_in_db, insert_api_key_in_db, get_user_info

from src.utils.logger import init_logger

logger = init_logger(debug=True)

# Using passlib for bcrypt hashing

router = APIRouter()

# ----------------------------------------------------------
# Password Hashing Configuration
# ----------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=APIKeyResponse)
async def register_user(req_data: RegisterRequest):
    """
    Register a new user with an email and password. Steps:
      1. Hash the user's password and store in MongoDB.
      2. Generate a new API Key and insert into PostgreSQL.
      3. Return the generated API key to the user.

      :param req_data: RegisterRequest, containing email and password.
        :return: APIKeyResponse

    If the user already exists, return a 400 Bad Request error.
    """

    hashed_pw = pwd_context.hash(req_data.password)

    created = create_user_in_db(req_data.email, hashed_pw)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists or error creating user."
        )

    db_response = insert_api_key_in_db(req_data.email)

    return APIKeyResponse(
        api_key=db_response[0],
        message="User registered successfully. Copy your API Key and keep it safe! IT WON'T BE SHOWN AGAIN.",
        account_type=db_response[1]
    )


@router.post("/login", response_model=APIKeyResponse)
async def login_user(req_data: RegisterRequest):
    """
    Login an existing user with an email and password. Steps:
      1. Verify the user's email and password.
      2. Return JWT to authenticate the user.

      :param req_data: RegisterRequest, containing email and password.
        :return: APIKeyResponse

    If the user does not exist or the password is incorrect, return a 400 Bad Request error.
    """
    is_valid = _verify_user_credentials(req_data.email, req_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password."
        )
    jwt_token = _generate_jwt_for_user(req_data.email)

    logger.info(f"User {req_data.email} logged in successfully.")

    return APIKeyResponse(
        token=jwt_token,
        message="Welcome back!"
    )


# ------------------------------
# Private helper functions
# ------------------------------
def _verify_user_credentials(email: str, password: str) -> bool:
    """
    Verifies that a user exists in MongoDB and that the provided password matches.

    :param email: The user's email.
    :param password: The plaintext password to check.
    :return: True if the credentials are valid, False otherwise.
    """

    user = get_user_info(email)
    if not user:
        return False  # No such user

    hashed_pw = user.get("password")
    return pwd_context.verify(password, hashed_pw)


def _generate_jwt_for_user(user_email: str) -> str:
    """
    Generates a JWT token for the given user.

    :param user_email: The user's email for whom the token is generated.
    :return: The JWT token as a string.
    """
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to sign JWT due to missing SECRET_KEY."
        )

    # Example: expires in 1 hour
    token = jwt.encode(
        {"sub": user_email, "exp": int(time.time()) + 3600},
        SECRET_KEY,
        algorithm="HS256"
    )
    return token
