"""
Report generation endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.services.report_service import generate_pdf_report, generate_html_report

router = APIRouter()


@router.get("/{scan_id}/pdf")
async def download_pdf_report(
    scan_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    PDF 보고서 다운로드
    
    - **scan_id**: 스캔 ID
    """
    # Verify scan ownership
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = scan_result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔을 찾을 수 없습니다"
        )
    
    # Get vulnerabilities
    vuln_result = await db.execute(
        select(Vulnerability).where(Vulnerability.scan_id == scan_id)
    )
    vulnerabilities = vuln_result.scalars().all()
    
    # Generate PDF
    pdf_buffer = await generate_pdf_report(scan, vulnerabilities)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=securescan_report_{scan_id}.pdf"
        }
    )


@router.get("/{scan_id}/html")
async def download_html_report(
    scan_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    HTML 보고서 다운로드
    
    - **scan_id**: 스캔 ID
    """
    # Verify scan ownership
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id)
    )
    scan = scan_result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔을 찾을 수 없습니다"
        )
    
    # Get vulnerabilities
    vuln_result = await db.execute(
        select(Vulnerability).where(Vulnerability.scan_id == scan_id)
    )
    vulnerabilities = vuln_result.scalars().all()
    
    # Generate HTML
    html_content = await generate_html_report(scan, vulnerabilities)
    
    return StreamingResponse(
        iter([html_content.encode()]),
        media_type="text/html",
        headers={
            "Content-Disposition": f"attachment; filename=securescan_report_{scan_id}.html"
        }
    )

