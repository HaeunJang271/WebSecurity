"""
Server-Side Request Forgery (SSRF) vulnerability checker
"""
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from app.scanner.checks.base import BaseChecker


class SSRFChecker(BaseChecker):
    """
    Check for Server-Side Request Forgery (SSRF) vulnerabilities
    """
    
    vuln_type = "ssrf"
    
    # SSRF payloads targeting internal resources
    PAYLOADS = [
        'http://localhost/',
        'http://127.0.0.1/',
        'http://[::1]/',
        'http://0.0.0.0/',
        'http://0/',
        'http://localhost:22/',
        'http://localhost:3306/',
        'http://127.0.0.1:6379/',
        'http://169.254.169.254/',  # AWS metadata
        'http://169.254.169.254/latest/meta-data/',
        'http://metadata.google.internal/',  # GCP metadata
        'http://100.100.100.200/latest/meta-data/',  # Alibaba Cloud
        'file:///etc/passwd',
        'file:///c:/windows/win.ini',
        'dict://localhost:11211/',
        'gopher://localhost:6379/',
    ]
    
    # Parameter names that commonly accept URLs
    URL_PARAMS = [
        'url', 'uri', 'link', 'src', 'source', 'dest', 'destination',
        'redirect', 'redirect_url', 'redirect_uri', 'return', 'return_url',
        'next', 'target', 'path', 'file', 'document', 'page', 'load',
        'fetch', 'proxy', 'image', 'img', 'resource', 'callback',
        'continue', 'goto', 'feed', 'host', 'site', 'ref', 'reference'
    ]
    
    # Patterns indicating SSRF might have worked
    SUCCESS_PATTERNS = [
        'root:',  # /etc/passwd
        '[fonts]',  # win.ini
        'ssh-',  # SSH banner
        'mysql',  # MySQL banner
        'redis',  # Redis banner
        'ami-id',  # AWS metadata
        'instance-id',
        'metadata',
        'compute_zone',  # GCP metadata
    ]
    
    # Error patterns that might indicate SSRF attempt was blocked or URL was processed
    INTERESTING_PATTERNS = [
        'connection refused',
        'connection timed out',
        'couldn\'t connect',
        'unable to connect',
        'failed to open',
        'invalid url',
        'url not found',
        'cannot fetch',
    ]
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for SSRF vulnerabilities
        """
        vulnerabilities = []
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Check existing URL-like parameters
        for param_name, param_values in params.items():
            param_lower = param_name.lower()
            
            # Check if parameter looks like it accepts URLs
            is_url_param = any(url_param in param_lower for url_param in self.URL_PARAMS)
            
            # Also check if current value looks like a URL
            for value in param_values:
                if value.startswith(('http://', 'https://', '//')):
                    is_url_param = True
                    break
            
            if is_url_param:
                vulns = await self._test_ssrf_param(session, url, param_name)
                vulnerabilities.extend(vulns)
        
        # If no URL params found, try common ones
        if not vulnerabilities and not params:
            for param_name in self.URL_PARAMS[:5]:
                vulns = await self._test_ssrf_param(session, url, param_name)
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def _test_ssrf_param(
        self,
        session: aiohttp.ClientSession,
        url: str,
        param: str
    ) -> List[Dict[str, Any]]:
        """
        Test a parameter for SSRF vulnerability
        """
        vulnerabilities = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        for payload in self.PAYLOADS[:6]:  # Test first 6 payloads
            test_url = f"{base_url}?{param}={payload}"
            
            try:
                async with session.get(
                    test_url,
                    timeout=aiohttp.ClientTimeout(total=15),
                    ssl=False,
                    allow_redirects=False
                ) as response:
                    text = await response.text()
                    text_lower = text.lower()
                    
                    # Check for success patterns (actual SSRF)
                    for pattern in self.SUCCESS_PATTERNS:
                        if pattern.lower() in text_lower:
                            vulnerabilities.append(self.create_vulnerability(
                                name="Server-Side Request Forgery (SSRF)",
                                severity="critical",
                                url=url,
                                description=f"파라미터 '{param}'에서 SSRF 취약점이 발견되었습니다. "
                                           f"공격자가 서버를 통해 내부 네트워크에 접근하거나 "
                                           f"클라우드 메타데이터를 탈취할 수 있습니다.",
                                evidence=f"Payload: {payload}\n"
                                        f"Success indicator found: {pattern}",
                                parameter=param,
                                method="GET",
                                recommendation="1. 사용자 입력 URL을 화이트리스트로 검증하세요.\n"
                                              "2. 내부 IP 주소와 localhost 접근을 차단하세요.\n"
                                              "3. DNS rebinding 공격을 방지하세요.\n"
                                              "4. 불필요한 URL 스킴(file://, gopher:// 등)을 차단하세요.",
                                references=[
                                    "https://owasp.org/www-community/attacks/Server_Side_Request_Forgery",
                                    "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"
                                ],
                                cwe_id="CWE-918",
                                cvss_score=9
                            ))
                            return vulnerabilities
                    
                    # Check for error patterns (potential SSRF)
                    for pattern in self.INTERESTING_PATTERNS:
                        if pattern in text_lower:
                            vulnerabilities.append(self.create_vulnerability(
                                name="Potential SSRF",
                                severity="medium",
                                url=url,
                                description=f"파라미터 '{param}'에서 잠재적 SSRF 취약점이 의심됩니다. "
                                           f"서버가 사용자 제공 URL을 처리하는 것으로 보입니다.",
                                evidence=f"Payload: {payload}\n"
                                        f"Error pattern found: {pattern}",
                                parameter=param,
                                method="GET",
                                recommendation="1. URL 입력을 검증하고 필터링하세요.\n"
                                              "2. 외부 요청 시 타임아웃과 속도 제한을 적용하세요.\n"
                                              "3. 응답 내용을 사용자에게 직접 노출하지 마세요.",
                                references=[
                                    "https://owasp.org/www-community/attacks/Server_Side_Request_Forgery"
                                ],
                                cwe_id="CWE-918",
                                cvss_score=6
                            ))
                            return vulnerabilities
                            
            except aiohttp.ClientTimeout:
                # Timeout might indicate the server is trying to connect
                continue
            except Exception:
                continue
        
        return vulnerabilities

