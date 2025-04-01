from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

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