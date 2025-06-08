from pymongo import MongoClient
from datetime import datetime
import os
import asyncio

# You can set MONGODB_URI in your environment, or default to localhost
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client["shadowai"]
history_collection = db["history"]

def save_to_history(
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
        # If in an async context, run in thread pool
        if asyncio.get_event_loop().is_running():
            asyncio.get_event_loop().run_in_executor(None, history_collection.insert_one, doc)
        else:
            history_collection.insert_one(doc)
    except Exception as e:
        print(f"[MongoDB] Failed to log history: {e}")
        import traceback
        traceback.print_exc()
        # Optionally, write to a local fallback file for debugging
        try:
            with open("mongo_history_fallback.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {feature} | {str(e)} | {doc}\n")
        except Exception as file_e:
            print(f"[MongoDB] Also failed to write fallback log: {file_e}")

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
