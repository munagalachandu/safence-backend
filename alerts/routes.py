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
    limit: int = Query(10)
):
    filter_query = {}
    if severity:
        filter_query["severity"] = {"$regex": severity, "$options": "i"}
    if status:
        filter_query["status"] = {"$regex": status, "$options": "i"}
    if device_id:
        filter_query["device_id"] = device_id

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
