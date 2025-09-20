from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

router = APIRouter()

MONGODB_URL = "mongodb+srv://sih:sih123@cluster0.ga6g9fv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.safence
cameras_collection = db.cameras


@router.get("/")
async def get_cameras():
    cameras = []
    async for camera in cameras_collection.find():
        camera["_id"] = str(camera["_id"])
        camera["last_activity"] = camera["last_activity"].isoformat() + "Z"
        cameras.append(camera)
    return cameras


@router.get("/{camera_id}/snapshot")
async def get_camera_snapshot(camera_id: str):
    return {
        "camera_id": camera_id,
        "snapshot_url": f"https://picsum.photos/640/480?random={camera_id}",
        "timestamp": datetime.now().isoformat() + "Z"
    }

