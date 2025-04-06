from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    width = Column(Integer, nullable=False)  # X dimension
    height = Column(Integer, nullable=False)  # Y dimension
    depth = Column(Integer, nullable=False)   # Z dimension
    max_weight = Column(Float, nullable=False)
    current_weight = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    zone = Column(String, default="general")  # Added zone for preferred placement
    
    # Relationship with Items
    items = relationship("Item", back_populates="container")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "max_weight": self.max_weight,
            "current_weight": self.current_weight,
            "is_active": self.is_active,
            "zone": self.zone
        }

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="")
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    width = Column(Integer, nullable=True)  # Added dimensions for placement
    depth = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    priority = Column(Integer, default=1)  # 1 (low) to 5 (high)
    is_fragile = Column(Boolean, default=False)
    preferred_zone = Column(String, default="general")  # Added preferred zone
    category = Column(String, default="general")  # Added category for grouping
    status = Column(String, default="AVAILABLE")  # AVAILABLE, CONSUMED, EXPIRED
    expiry_date = Column(DateTime, nullable=True)
    consumed_date = Column(DateTime, nullable=True)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    position_z = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with Container
    container = relationship("Container", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "volume": self.volume,
            "width": self.width,
            "depth": self.depth,
            "height": self.height,
            "priority": self.priority,
            "is_fragile": self.is_fragile,
            "preferred_zone": self.preferred_zone,
            "category": self.category,
            "status": self.status,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "consumed_date": self.consumed_date.isoformat() if self.consumed_date else None,
            "container_id": self.container_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z
        }

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 