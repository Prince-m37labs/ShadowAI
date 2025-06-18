from pymongo import MongoClient
from datetime import datetime
import os
import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# You can set MONGODB_URI in your environment, or default to localhost
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

def get_mongo_client():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Log connection type
        if "mongodb+srv" in MONGODB_URI:
            logger.info("Connecting to MongoDB Atlas.")
        else:
            logger.info("Connecting to local MongoDB instance.")
        # Verify the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

# Initialize MongoDB connection
try:
    client = get_mongo_client()
    db = client["shadowai"]
    history_collection = db["history"]
    
    # Create text index if it doesn't exist
    def ensure_text_index():
        try:
            # Check if text index exists
            existing_indexes = history_collection.list_indexes()
            has_text_index = any(index.get('name') == 'input_text_metadata.context_text' 
                               for index in existing_indexes)
            
            if not has_text_index:
                logger.info("Creating text index on history collection...")
                history_collection.create_index([
                    ("input", "text"),
                    ("metadata.context", "text")
                ], name="input_text_metadata.context_text")
                logger.info("Text index created successfully")
        except Exception as e:
            logger.error(f"Failed to create text index: {e}")
    
    ensure_text_index()
    logger.info("MongoDB collections initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB collections: {e}")
    raise

async def save_to_history_async(
    feature: str,
    user_input: str,
    claude_prompt: str,
    claude_response: str,
    response_time_ms: float = None,
    metadata: dict = None
):
    doc = {
        "feature": feature,
        "input": user_input,
        "claude_prompt": claude_prompt,
        "claude_response": claude_response,
        "timestamp": datetime.utcnow(),
    }
    if response_time_ms is not None:
        doc["response_time_ms"] = response_time_ms
    if metadata is not None:
        doc["metadata"] = metadata
    
    try:
        # Always use async execution
        await asyncio.get_event_loop().run_in_executor(None, history_collection.insert_one, doc)
        logger.info(f"Successfully saved history for feature: {feature}")
    except Exception as e:
        logger.error(f"[MongoDB] Failed to log history: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Write to a local fallback file for debugging
        try:
            with open("mongo_history_fallback.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {feature} | {str(e)} | {doc}\n")
        except Exception as file_e:
            logger.error(f"[MongoDB] Also failed to write fallback log: {file_e}")

async def save_to_history(
    feature: str,
    user_input: str,
    claude_prompt: str,
    claude_response: str,
    response_time_ms: float = None,
    metadata: dict = None
):
    logger.info(f"Attempting to save history for feature: {feature}")
    doc = {
        "feature": feature,
        "input": user_input,
        "claude_prompt": claude_prompt,
        "claude_response": claude_response,
        "timestamp": datetime.utcnow(),
    }
    if response_time_ms is not None:
        doc["response_time_ms"] = response_time_ms
    if metadata is not None:
        doc["metadata"] = metadata
    
    try:
        logger.info(f"Preparing to insert document into MongoDB: {doc}")
        # Use run_in_executor to run the blocking MongoDB operation
        result = await asyncio.get_running_loop().run_in_executor(None, history_collection.insert_one, doc)
        logger.info(f"Successfully saved history for feature: {feature}, document ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"[MongoDB] Failed to log history: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Write to a local fallback file for debugging
        try:
            with open("mongo_history_fallback.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {feature} | {str(e)} | {doc}\n")
        except Exception as file_e:
            logger.error(f"[MongoDB] Also failed to write fallback log: {file_e}")
        raise  # Re-raise the exception to handle it in the route

# New: Retrieve history with filters
def get_history(
    feature: str = None,
    session_id: str = None,
    model: str = None,
    mode: str = None,
    file_type: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 50
):
    query = {}
    if feature:
        query["feature"] = feature
    if session_id:
        query["metadata.session_id"] = session_id
    if model:
        query["metadata.model"] = model
    if mode:
        query["metadata.mode"] = mode
    if file_type:
        query["metadata.file_type"] = file_type
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date
    return list(history_collection.find(query).sort("timestamp", -1).limit(limit))


# Retrieve similar history using MongoDB text search
async def find_similar_history(feature: str, user_input: str, context: str, score_threshold: float = 2.0):
    from pymongo import TEXT

    try:
        # Ensure text index exists on input and metadata fields (run this manually once in DB):
        # db.history.create_index([("input", TEXT), ("metadata.context", TEXT)])

        combined_query = f"{user_input} {context}"
        logger.info(f"[Cache Lookup] Searching for similar history with query: {combined_query[:100]}...")
        
        # Use run_in_executor for MongoDB operations
        result = await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: history_collection.find_one(
            {
                "$text": {"$search": combined_query},
                "feature": feature
            },
            sort=[("score", {"$meta": "textScore"})],
            projection={"claude_response": 1, "input": 1, "score": {"$meta": "textScore"}}
            )
        )

        if result and result.get("score", 0) > score_threshold:
            logger.info(f"[Cache Hit] Found similar query in DB with score {result['score']:.2f}")
            logger.info(f"[Cache Hit] Original input: {result['input'][:100]}...")
            return result["claude_response"]
        else:
            if result:
                logger.info(f"[Cache Miss] Found result but score {result.get('score', 0):.2f} below threshold {score_threshold}")
            else:
                logger.info("[Cache Miss] No similar history found in database")
    except Exception as e:
        logger.warning(f"[Cache Lookup] Failed to search similar history: {e}")

    return None
