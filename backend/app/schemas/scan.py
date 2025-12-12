"""
Scan schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field

from app.models.scan import ScanStatus


class ScanCreate(BaseModel):
    """Schema for creating a new scan"""
    target_url: str = Field(..., description="대상 URL")
    scan_type: str = Field(default="full", description="스캔 유형: quick, full, custom")
    scan_depth: int = Field(default=3, ge=1, le=10, description="스캔 깊이")


class ScanResponse(BaseModel):
    """Schema for scan response"""
    id: int
    target_url: str
    target_domain: str
    scan_type: str
    scan_depth: int
    status: ScanStatus
    progress: int
    
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ScanListResponse(BaseModel):
    """Schema for list of scans"""
    scans: List[ScanResponse]
    total: int
    page: int
    page_size: int


class ScanProgress(BaseModel):
    """Schema for scan progress update"""
    scan_id: int
    status: ScanStatus
    progress: int
    message: Optional[str] = None

