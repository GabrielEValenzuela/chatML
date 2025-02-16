"""
    This module implements the handling of database connections for the API.
    The module provides functions to interact with PostgreSQL and MongoDB databases.
    
    PostgreSQL is used to store API keys, while MongoDB is used to store user information.
    The reason for using two different databases is to demonstrate how to work with multiple databases in a single application and 
    take advantage of the strengths of each database. PostgreSQL is useful for structured data and transactions, while MongoDB is
    useful for unstructured data and scalability.
"""

import os
import secrets
import psycopg2

from src.utils.logger import init_logger

from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from typing import Any, Tuple
from functools import lru_cache

API_KEY_LENGTH = 16
# This is only for testing purposes, do not use this in production!
CONDITION = "gmail.com"


logger = init_logger(debug=True)


@lru_cache(maxsize=1)
def get_postgres_connection():
    """
    Returns a singleton psycopg2 connection to the PostgreSQL database.
    If the function is called multiple times, the same connection instance is returned.
    """
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "api_db")
    user = os.getenv("POSTGRES_USER", "api_user")
    password = os.getenv("POSTGRES_PASSWORD", "api_password")

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        return conn
    except psycopg2.Error as e:
        raise e


@lru_cache(maxsize=1)
def get_mongo_client():
    """
    Returns a singleton MongoClient instance for MongoDB.

    Uses the environment variable MONGO_URI to connect.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(mongo_uri)

# ----------------------------------------------------------
# PostgreSQL Database Functions
# ----------------------------------------------------------


def get_api_key_info(api_key: str) -> dict:
    """
    Returns the API key information from the PostgreSQL database using a singleton connection.
    """
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM api_keys WHERE api_key = %s",
        (api_key,)
    )
    api_key_info = cursor.fetchone()
    cursor.close()
    return api_key_info


def insert_api_key_in_db(user_email: str) -> Tuple[str, str]:
    """
    Inserts a new API key record into PostgreSQL for the given user,
    randomly assigning FREEMIUM or PREMIUM account_type.

    :param user_email: The user's email.
    :return: The newly created API key, or an empty string if insertion failed.
    """
    new_api_key = secrets.token_hex(API_KEY_LENGTH)
    try:
        conn = get_postgres_connection()
        account_type = "PREMIUM" if CONDITION in user_email else "FREEMIUM"
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO api_keys (api_key, user_email, account_type)
                    VALUES (%s, %s, %s)
                    RETURNING api_key
                """, (new_api_key, user_email, account_type))

                row = cur.fetchone()
                if row:
                    logger.info(
                        f"New API key {new_api_key} created for {user_email}. "
                        f"Account type: {account_type}"
                    )
                    return (row[0], account_type)
                return ""
    except Exception as e:
        logger.error(f"Error inserting API key in DB: {e}")
        return ""

# ----------------------------------------------------------
# MongoDB Database Functions
# ----------------------------------------------------------


def get_mongo_collection(collection_name: str) -> Any:
    """
    Returns a MongoDB collection reference from a singleton MongoClient.

    :param collection_name: The name of the collection to retrieve.
    :return: A reference to the MongoDB collection.

    """
    mongo_db_name = os.getenv("MONGO_DB", "api_user_db")
    client = get_mongo_client()  # same instance every time
    db = client[mongo_db_name]
    return db[collection_name]


def get_user_info(email: str) -> dict:
    """
    Returns user information from the MongoDB database using a singleton connection.

    :param email: The email address of the user.
    :return: A dictionary with user information.
    """
    collection = get_mongo_collection("users")
    return collection.find_one({"email": email})


def create_user_in_db(email: str, password: str) -> bool:
    """
    Inserts a new user record into MongoDB.

    :param email: The user's email.
    :param password: The user's plaintext password.
    :return: True if the user was successfully created, False otherwise.
    """
    users_collection = get_mongo_collection("users")

    try:
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return False  # User already exists

        users_collection.insert_one({
            "email": email,
            "password": password,
        })
        logger.info(f"New user created: {email}")
        return True

    except Exception as e:
        logger.error(f"Error creating user in DB: {e}")
        return False
