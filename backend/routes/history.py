from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from db import get_history

router = APIRouter()

@router.get("/history")
async def history(
    feature: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Retrieve logs from history with flexible filters.
    """
    results = get_history(
        feature=feature,
        session_id=session_id,
        model=model,
        mode=mode,
        file_type=file_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    # Convert ObjectId and datetime to string for JSON serialization
    for r in results:
        r["_id"] = str(r["_id"])
        if "timestamp" in r:
            r["timestamp"] = r["timestamp"].isoformat()
    return {"results": results}
