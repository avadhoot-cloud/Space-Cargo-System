from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ContainerBase(BaseModel):
    name: str
    width: float
    height: float
    depth: float
    max_weight: float
    zone: str

class ContainerCreate(ContainerBase):
    pass

class Container(ContainerBase):
    id: int
    used_volume: float
    used_weight: float
    is_full: bool

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    width: float
    height: float
    depth: float
    weight: float
    priority: int = Field(default=50, ge=0, le=100)
    preferred_zone: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    is_placed: bool
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None
    placement_date: Optional[datetime] = None
    container_id: Optional[int] = None

    class Config:
        from_attributes = True

class PlacementHistoryBase(BaseModel):
    item_id: int
    container_id: int
    success: bool
    reason: Optional[str] = None

class PlacementHistoryCreate(PlacementHistoryBase):
    pass

class PlacementHistory(PlacementHistoryBase):
    id: int
    placement_date: datetime

    class Config:
        from_attributes = True

class PlacementRecommendation(BaseModel):
    item_id: int
    item_name: str
    container_id: int
    container_name: str
    reasoning: str
    score: float

class PlacementStatistics(BaseModel):
    total_items_placed: int
    space_utilization: float
    success_rate: float
    efficiency: float
    priority_satisfaction: float
    zone_match_rate: float
    container_utilization: List[dict]

class PlacementResponse(BaseModel):
    success: bool
    message: str
    container_id: Optional[int] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None 