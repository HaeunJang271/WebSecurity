"""
Scan model for vulnerability scanning jobs
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class ScanStatus(str, Enum):
    """Scan status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scan(Base):
    """Scan model for tracking vulnerability scans"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Target information
    target_url = Column(String(2048), nullable=False)
    target_domain = Column(String(255), nullable=False)
    
    # Scan configuration
    scan_type = Column(String(50), default="full")  # quick, full, custom
    scan_depth = Column(Integer, default=3)
    
    # Status tracking
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    
    # Results summary
    total_vulnerabilities = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan(id={self.id}, target={self.target_domain}, status={self.status})>"

