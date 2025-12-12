"""
Scan endpoints
"""
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.scan import Scan, ScanStatus
from app.schemas.scan import ScanCreate, ScanResponse, ScanListResponse

router = APIRouter()


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    새 스캔 시작
    
    - **target_url**: 스캔할 대상 URL
    - **scan_type**: 스캔 유형 (quick, full, custom)
    - **scan_depth**: 스캔 깊이 (1-10)
    """
    # Validate URL
    target_url = scan_data.target_url
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
    
    domain = extract_domain(target_url)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 URL입니다"
        )
    
    # Create scan record
    scan = Scan(
        user_id=user_id,
        target_url=target_url,
        target_domain=domain,
        scan_type=scan_data.scan_type,
        scan_depth=scan_data.scan_depth,
        status=ScanStatus.PENDING
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Start scan in background
    from app.services.scanner_service import run_scan
    background_tasks.add_task(run_scan, scan.id)
    
    return scan


@router.get("", response_model=ScanListResponse)
async def list_scans(
    page: int = 1,
    page_size: int = 10,
    status: Optional[ScanStatus] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    스캔 목록 조회
    
    - **page**: 페이지 번호
    - **page_size**: 페이지 크기
    - **status**: 상태 필터 (선택)
    """
    # Build query
    query = select(Scan).where(Scan.user_id == user_id)
    
    if status:
        query = query.where(Scan.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(Scan).where(Scan.user_id == user_id)
    if status:
        count_query = count_query.where(Scan.status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = query.order_by(Scan.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return ScanListResponse(
        scans=scans,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    스캔 상세 조회
    
    - **scan_id**: 스캔 ID
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔을 찾을 수 없습니다"
        )
    
    return scan


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    스캔 삭제
    
    - **scan_id**: 스캔 ID
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔을 찾을 수 없습니다"
        )
    
    await db.delete(scan)
    await db.commit()


@router.post("/{scan_id}/cancel", response_model=ScanResponse)
async def cancel_scan(
    scan_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    스캔 취소
    
    - **scan_id**: 스캔 ID
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔을 찾을 수 없습니다"
        )
    
    if scan.status not in [ScanStatus.PENDING, ScanStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="진행 중인 스캔만 취소할 수 있습니다"
        )
    
    scan.status = ScanStatus.CANCELLED
    scan.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(scan)
    
    return scan

