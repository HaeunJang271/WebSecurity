"""
Vulnerability endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.scan import Scan
from app.models.vulnerability import Vulnerability, Severity
from app.schemas.vulnerability import VulnerabilityResponse, VulnerabilityListResponse

router = APIRouter()


@router.get("/scan/{scan_id}", response_model=VulnerabilityListResponse)
async def get_scan_vulnerabilities(
    scan_id: int,
    severity: Optional[Severity] = None,
    vuln_type: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    스캔 취약점 목록 조회
    
    - **scan_id**: 스캔 ID
    - **severity**: 심각도 필터 (선택)
    - **vuln_type**: 취약점 유형 필터 (선택)
    """
    try:
        print(f"📋 Fetching vulnerabilities for scan {scan_id}, user {user_id}")
        
        # Verify scan ownership
        scan_result = await db.execute(
            select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
        )
        scan = scan_result.scalar_one_or_none()
        
        if not scan:
            print(f"❌ Scan {scan_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="스캔을 찾을 수 없습니다"
            )
    
        # Build query
        query = select(Vulnerability).where(Vulnerability.scan_id == scan_id)
        
        if severity:
            query = query.where(Vulnerability.severity == severity)
        if vuln_type:
            query = query.where(Vulnerability.vuln_type == vuln_type)
        
        query = query.order_by(
            # Order by severity (critical first)
            case(
                (Vulnerability.severity == Severity.CRITICAL, 1),
                (Vulnerability.severity == Severity.HIGH, 2),
                (Vulnerability.severity == Severity.MEDIUM, 3),
                (Vulnerability.severity == Severity.LOW, 4),
                else_=5
            )
        )
        
        result = await db.execute(query)
        vulnerabilities = result.scalars().all()
        
        print(f"✅ Found {len(vulnerabilities)} vulnerabilities for scan {scan_id}")
        
        # Count by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        
        for vuln in vulnerabilities:
            severity_counts[vuln.severity.value] += 1
        
        return VulnerabilityListResponse(
            vulnerabilities=vulnerabilities,
            total=len(vulnerabilities),
            critical=severity_counts["critical"],
            high=severity_counts["high"],
            medium=severity_counts["medium"],
            low=severity_counts["low"],
            info=severity_counts["info"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching vulnerabilities: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"취약점 조회 중 오류 발생: {str(e)}"
        )


@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    취약점 상세 조회
    
    - **vuln_id**: 취약점 ID
    """
    # Get vulnerability with scan ownership check
    result = await db.execute(
        select(Vulnerability)
        .join(Scan)
        .where(Vulnerability.id == vuln_id, Scan.user_id == user_id)
    )
    vuln = result.scalar_one_or_none()
    
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="취약점을 찾을 수 없습니다"
        )
    
    return vuln


@router.patch("/{vuln_id}/false-positive")
async def mark_false_positive(
    vuln_id: int,
    is_false_positive: bool,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    취약점 오탐 여부 설정
    
    - **vuln_id**: 취약점 ID
    - **is_false_positive**: 오탐 여부
    """
    result = await db.execute(
        select(Vulnerability)
        .join(Scan)
        .where(Vulnerability.id == vuln_id, Scan.user_id == user_id)
    )
    vuln = result.scalar_one_or_none()
    
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="취약점을 찾을 수 없습니다"
        )
    
    vuln.is_false_positive = 1 if is_false_positive else 0
    await db.commit()
    
    return {"message": "업데이트 완료", "is_false_positive": is_false_positive}

