"""
Main FastAPI application for the Similarity Detection API.

This module initializes and configures:
- ML Model (TransH)
- Database connections (PostgreSQL, MongoDB)
- Redis client for caching and rate limiting
- Load the FastAPI routes
"""

# ----------------------------------------------------------
# Standard Imports
# ----------------------------------------------------------
import datetime

# ----------------------------------------------------------
# uvicorn Imports
# ----------------------------------------------------------
import uvicorn

# ----------------------------------------------------------
# Router Imports
# ----------------------------------------------------------
from src.api.routes.home import router as home
from src.api.routes.session import router as session
from src.api.routes.service import router as service

# ----------------------------------------------------------
# FastAPI Imports
# ----------------------------------------------------------
from fastapi import FastAPI
from contextlib import asynccontextmanager

# ----------------------------------------------------------
# Project Imports
# ----------------------------------------------------------
from src.utils.logger import init_logger
from src.ml.model import TransHModel

from src.core.redis_client import get_redis_client
from src.core.database import get_mongo_collection, get_postgres_connection


from dotenv import load_dotenv

# ----------------------------------------------------------
# Logger Initialization
# ----------------------------------------------------------
logger = init_logger(debug=True)

# ----------------------------------------------------------
# Load Environment Variables
# ----------------------------------------------------------
load_dotenv()


@asynccontextmanager
async def lifespan_resources(app: FastAPI):
    """
    A lifespan context manager that initializes and provides shared instances of:
    - TransHModel (ML model)
    - PostgreSQL connection
    - MongoDB collection
    - Redis client

    These instances are stored in `app.state` and shared across requests.

    :param app: The FastAPI application instance.
    :yields: None. Sets up shared state, then cleans up on shutdown.
    """
    logger.info("🔄 Initializing application resources...")

    try:
        # 1️⃣ Load TransH Model
        logger.info("Loading TransH model...")
        start_time = datetime.datetime.now()
        model = TransHModel()
        model.load()
        end_time = datetime.datetime.now()
        logger.debug(f"Model paths: {model.model_path}, {model.triples_path}")
        logger.debug(f"Time to load model: {end_time - start_time}")
        app.state.transh_model = model
        logger.info("✅ TransH model loaded successfully.")

        # 2️⃣ Initialize PostgreSQL connection
        logger.info("Connecting to PostgreSQL...")
        postgres_conn = get_postgres_connection()
        app.state.postgres_conn = postgres_conn
        logger.info("✅ PostgreSQL connected.")

        # 3️⃣ Initialize MongoDB collection (assumes 'users' collection)
        logger.info("Connecting to MongoDB...")
        mongo_collection = get_mongo_collection("users")
        app.state.mongo_collection = mongo_collection
        logger.info("✅ MongoDB connected.")

        # 4️⃣ Initialize Redis client
        logger.info("Connecting to Redis...")
        redis_client = get_redis_client()
        app.state.redis_client = redis_client
        logger.info("✅ Redis connected.")

        # Hand control back to FastAPI (run app)
        yield

    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}")
        raise

    finally:
        # Cleanup resources when FastAPI shuts down
        logger.info("🔄 Cleaning up application resources...")

        # Close PostgreSQL connection
        if hasattr(app.state, "postgres_conn"):
            app.state.postgres_conn.close()
            logger.info("✅ PostgreSQL connection closed.")

        # Close MongoDB client
        if hasattr(app.state, "mongo_client"):
            app.state.mongo_client.close()
            logger.info("✅ MongoDB connection closed.")

        # Close Redis connection
        if hasattr(app.state, "redis_client"):
            app.state.redis_client.close()
            logger.info("✅ Redis connection closed.")

        logger.info("✅ Cleanup complete. Shutting down FastAPI application.")

# ----------------------------------------------------------
# Create FastAPI instance with lifespan
# ----------------------------------------------------------
app = FastAPI(lifespan=lifespan_resources)

app.include_router(home, tags=["home"])
app.include_router(session, tags=["session"])
app.include_router(service, tags=["similarity_service"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
