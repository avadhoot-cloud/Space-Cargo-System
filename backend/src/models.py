from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
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
            "is_active": self.is_active
        }

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="")
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    priority = Column(Integer, default=1)  # 1 (low) to 5 (high)
    is_fragile = Column(Boolean, default=False)
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
            "priority": self.priority,
            "is_fragile": self.is_fragile,
            "container_id": self.container_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z
        } 