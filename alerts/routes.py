from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional

router = APIRouter()

MONGODB_URL = "mongodb+srv://sih:sih123@cluster0.ga6g9fv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.safence
alerts_collection = db.alerts


@router.get("/")
async def get_alerts(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
    limit: int = Query(10),
    type: Optional[str] = Query(None),
     start_time: Optional[str] = Query(None, description="ISO8601 start time filter"),
    end_time: Optional[str] = Query(None, description="ISO8601 end time filter"),

):
    filter_query = {}
    if severity:
        filter_query["severity"] = {"$regex": severity, "$options": "i"}
    if status:
        filter_query["status"] = {"$regex": status, "$options": "i"}
    if device_id:
        filter_query["device_id"] = device_id
    if type:
        filter_query["type"] = {"$regex": type, "$options": "i"}
    if start_time or end_time:
        time_filter = {}
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                time_filter["$gte"] = start_dt
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time)
                time_filter["$lte"] = end_dt
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")

        filter_query["timestamp"] = time_filter
        
    alerts = []
    async for alert in alerts_collection.find(filter_query).sort("timestamp", -1).limit(limit):
        alert["_id"] = str(alert["_id"])
        alert["timestamp"] = alert["timestamp"].isoformat() + "Z"
        alerts.append(alert)
    return alerts


@router.patch("/{alert_id}")
async def update_alert(alert_id: str, status_update: dict):
    result = await alerts_collection.update_one(
        {"alert_id": alert_id},
        {"$set": {"status": status_update.get("status")}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert updated successfully"}

@router.get("/counts/summary")
async def get_alerts_counts_summary():
    # Aggregation pipeline to count by severity
    severity_pipeline = [
        {
            "$group": {
                "_id": "$severity",
                "count": {"$sum": 1}
            }
        }
    ]
    severity_counts = await alerts_collection.aggregate(severity_pipeline).to_list(length=None)
    severity_dict = {item["_id"].lower() if item["_id"] else "unknown": item["count"] for item in severity_counts}

    # Aggregation pipeline to count by status
    status_pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    status_counts = await alerts_collection.aggregate(status_pipeline).to_list(length=None)
    status_dict = {item["_id"].lower() if item["_id"] else "unknown": item["count"] for item in status_counts}

    return {
        "severity_counts": severity_dict,
        "status_counts": status_dict,
    }

    type_counts = await alerts_collection.aggregate(type_pipeline).to_list(length=None)
    type_dict = {item["_id"].lower() if item["_id"] else "unknown": item["count"] for item in type_counts}

    return {
        "severity_counts": severity_dict,
        "status_counts": status_dict,
        "type_counts": type_dict,
    }
