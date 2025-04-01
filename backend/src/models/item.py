from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    priority = Column(Integer, default=1)  # 1 (low) to 5 (high)
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)
    position_x = Column(Integer, nullable=True)
    position_y = Column(Integer, nullable=True)
    position_z = Column(Integer, nullable=True)
    is_fragile = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with Container
    container = relationship("Container", back_populates="items") 