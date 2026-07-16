from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.db.session import Base

class ExchangeConnection(Base):
    __tablename__ = "exchange_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    exchange = Column(String(50), nullable=False)  # "bingx", etc
    api_key_encrypted = Column(Text, nullable=False)  # Encrypted
    api_secret_encrypted = Column(Text, nullable=False)  # Encrypted
    is_active = Column(Boolean, default=True)
    last_connected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="exchange_connections")
