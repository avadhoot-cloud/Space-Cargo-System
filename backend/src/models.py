from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    width = Column(Integer)
    height = Column(Integer)
    depth = Column(Integer)
    max_weight = Column(Float)
    current_weight = Column(Float, default=0.0)
    zone = Column(String, default="")
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "max_weight": self.max_weight,
            "current_weight": self.current_weight,
            "zone": self.zone,
            "is_active": self.is_active
        }

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="")
    weight = Column(Float)
    width = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    depth = Column(Float, default=0.0)
    volume = Column(Float)
    priority = Column(Integer, default=1)
    is_fragile = Column(Boolean, default=False)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    position_z = Column(Integer, nullable=True)
    expiry_date = Column(String, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    preferred_zone = Column(String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "volume": self.volume,
            "priority": self.priority,
            "is_fragile": self.is_fragile,
            "container_id": self.container_id,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "expiry_date": self.expiry_date,
            "usage_limit": self.usage_limit,
            "preferred_zone": self.preferred_zone
        } 