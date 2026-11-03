from fastapi import APIRouter

router = APIRouter()


@router.get("")
@router.get("/")
async def health_check():
    """Basic health check placeholder"""
    return {
        "status": "online",
        "service": "threat-intel-aggregator"
    }