from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict

router = APIRouter()

MONGODB_URL = "mongodb+srv://sih:sih123@cluster0.ga6g9fv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.safence
devices_collection = db.devices


@router.get("/{device_id}")
async def get_device(device_id: str):
    device = await devices_collection.find_one({"device_id": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device["_id"] = str(device["_id"])
    device["last_heartbeat"] = device["last_heartbeat"].isoformat() + "Z"
    return device


@router.patch("/{device_id}")
async def update_device(device_id: str, device_update: Dict):
    result = await devices_collection.update_one(
        {"device_id": device_id},
        {"$set": device_update}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device updated successfully"}
