"""
This module contains Pydantic models for the API.
These models are used to validate request and response payloads.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, Union, List, Tuple

# ----------------------------------------------------------
# Placeholder Models for User Registration/Login
# ----------------------------------------------------------


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ----------------------------------------------------------
# Placeholder Model for API Key or JWT Responses
# ----------------------------------------------------------


class APIKeyResponse(BaseModel):
    api_key: Optional[str] = None
    token: Optional[str] = None
    message: Optional[str] = None
    account_type: Optional[str] = None

# ----------------------------------------------------------
# New: Models for Similarity Service
# ----------------------------------------------------------


class SimilarityRequest(BaseModel):
    """
    Request model for the similarity service.
    These fields align with what main.py expects:
      - entity_input: The entity label (str) or ID to compare.
      - relation_idx: An integer index for the relation (default: 5).
      - top_k: The number of top entities to retrieve (default: 10).
    """
    api_key: str
    entity_input: Union[int, str]


class SimilarityResponse(BaseModel):
    """
    Response model returned by the similarity service.
    main.py calls `SimilarityResponse(probability=probability)`,
    so we store a single float in `probability`.
    """
    cache: bool
    result: List[Tuple[str, float]]
