from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)
    max_weight = Column(Float)
    zone = Column(String)
    used_volume = Column(Float, default=0.0)
    used_weight = Column(Float, default=0.0)
    is_full = Column(Boolean, default=False)
    
    # Relationships
    items = relationship("Item", back_populates="container")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)
    weight = Column(Float)
    priority = Column(Integer, default=50)
    preferred_zone = Column(String, nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    position_z = Column(Float, nullable=True)
    is_placed = Column(Boolean, default=False)
    placement_date = Column(DateTime, nullable=True)
    
    # Foreign keys
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)
    
    # Relationships
    container = relationship("Container", back_populates="items")

class PlacementHistory(Base):
    __tablename__ = "placement_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    container_id = Column(Integer, ForeignKey("containers.id"))
    placement_date = Column(DateTime)
    success = Column(Boolean)
    reason = Column(String, nullable=True)
    
    # Relationships
    item = relationship("Item")
    container = relationship("Container") 