"""
Base class for security checkers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp


class BaseChecker(ABC):
    """
    Abstract base class for all security checkers
    """
    
    # Vulnerability type identifier
    vuln_type: str = "unknown"
    
    # Common user agents for testing
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "SecureScan Security Scanner/1.0"
    ]
    
    @abstractmethod
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Run security check on a URL
        
        Returns list of vulnerability dictionaries
        """
        pass
    
    async def check_form(
        self,
        session: aiohttp.ClientSession,
        form_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run security check on a form
        
        Default implementation returns empty list.
        Override in subclasses that need form testing.
        """
        return []
    
    def create_vulnerability(
        self,
        name: str,
        severity: str,
        url: str,
        description: str,
        evidence: Optional[str] = None,
        parameter: Optional[str] = None,
        method: str = "GET",
        recommendation: Optional[str] = None,
        references: Optional[List[str]] = None,
        cwe_id: Optional[str] = None,
        cvss_score: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized vulnerability dictionary
        """
        return {
            "type": self.vuln_type,
            "name": name,
            "severity": severity,
            "url": url,
            "description": description,
            "evidence": evidence,
            "parameter": parameter,
            "method": method,
            "recommendation": recommendation,
            "references": references or [],
            "cwe_id": cwe_id,
            "cvss_score": cvss_score
        }
    
    async def safe_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        """
        Make a safe HTTP request with error handling
        """
        try:
            kwargs.setdefault('timeout', aiohttp.ClientTimeout(total=10))
            kwargs.setdefault('ssl', False)
            kwargs.setdefault('headers', {})
            kwargs['headers'].setdefault('User-Agent', self.USER_AGENTS[0])
            
            async with session.request(method, url, **kwargs) as response:
                return response
        except Exception:
            return None

