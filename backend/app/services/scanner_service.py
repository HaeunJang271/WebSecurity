"""
Scanner service for orchestrating vulnerability scans
"""
import asyncio
from datetime import datetime
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.vulnerability import Vulnerability, Severity
from app.scanner import SecurityScanner


async def run_scan(scan_id: int):
    """
    Run a vulnerability scan in the background
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get scan record
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()
            
            if not scan:
                return
            
            # Update status to running
            scan.status = ScanStatus.RUNNING
            scan.started_at = datetime.utcnow()
            await db.commit()
            
            # Initialize scanner
            scanner = SecurityScanner(scan.target_url, scan.scan_depth)
            
            # Run all security checks
            vulnerabilities = await scanner.run_full_scan(
                progress_callback=lambda p: update_progress(db, scan, p)
            )
            
            # Save vulnerabilities
            for vuln_data in vulnerabilities:
                vuln = Vulnerability(
                    scan_id=scan_id,
                    vuln_type=vuln_data["type"],
                    name=vuln_data["name"],
                    severity=Severity(vuln_data["severity"]),
                    cvss_score=vuln_data.get("cvss_score"),
                    affected_url=vuln_data["url"],
                    affected_parameter=vuln_data.get("parameter"),
                    http_method=vuln_data.get("method", "GET"),
                    description=vuln_data["description"],
                    evidence=vuln_data.get("evidence"),
                    recommendation=vuln_data.get("recommendation"),
                    references=vuln_data.get("references"),
                    cwe_id=vuln_data.get("cwe_id")
                )
                db.add(vuln)
            
            # Update scan summary
            scan.total_vulnerabilities = len(vulnerabilities)
            scan.critical_count = sum(1 for v in vulnerabilities if v["severity"] == "critical")
            scan.high_count = sum(1 for v in vulnerabilities if v["severity"] == "high")
            scan.medium_count = sum(1 for v in vulnerabilities if v["severity"] == "medium")
            scan.low_count = sum(1 for v in vulnerabilities if v["severity"] == "low")
            scan.info_count = sum(1 for v in vulnerabilities if v["severity"] == "info")
            
            scan.status = ScanStatus.COMPLETED
            scan.progress = 100
            scan.completed_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            # Update scan with error
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            await db.commit()


async def update_progress(db: AsyncSession, scan: Scan, progress: int):
    """Update scan progress"""
    scan.progress = progress
    await db.commit()

