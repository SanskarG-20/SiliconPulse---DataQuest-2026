from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class RadarStatus(BaseModel):
    company: str
    status: str
    trend: str

@router.get("/", response_model=List[RadarStatus])
async def get_radar():
    # TODO: Implement radar data retrieval
    return []

@router.get("/{company}", response_model=RadarStatus)
async def get_company_radar(company: str):
    # TODO: Implement single company radar retrieval
    pass
