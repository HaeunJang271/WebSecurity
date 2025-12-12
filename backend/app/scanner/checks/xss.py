"""
Cross-Site Scripting (XSS) vulnerability checker
"""
import re
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
import aiohttp

from app.scanner.checks.base import BaseChecker


class XSSChecker(BaseChecker):
    """
    Check for Cross-Site Scripting (XSS) vulnerabilities
    """
    
    vuln_type = "xss"
    
    # XSS payloads
    PAYLOADS = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        '<svg onload=alert("XSS")>',
        '"><script>alert("XSS")</script>',
        "'-alert('XSS')-'",
        '<img src="x" onerror="alert(1)">',
        '<body onload=alert("XSS")>',
        '<iframe src="javascript:alert(1)">',
        '<input onfocus=alert(1) autofocus>',
        '{{constructor.constructor("alert(1)")()}}',
        '${alert(1)}',
        '<a href="javascript:alert(1)">click</a>',
        '<div onmouseover="alert(1)">hover</div>',
    ]
    
    # Unique markers for detection
    MARKER = "SECURESCAN_XSS_TEST_"
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for XSS vulnerabilities
        """
        vulnerabilities = []
        
        # Parse URL parameters
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            # Try with common parameter names
            test_params = ['q', 'search', 'query', 'keyword', 'name', 'input', 'text', 'message']
            for param in test_params:
                vulns = await self._test_reflected_xss(session, url, param)
                vulnerabilities.extend(vulns)
        else:
            # Test existing parameters
            for param in params.keys():
                vulns = await self._test_reflected_xss(session, url, param)
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def check_form(
        self,
        session: aiohttp.ClientSession,
        form_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check form for XSS vulnerabilities
        """
        vulnerabilities = []
        
        action_url = form_data.get('action', '')
        method = form_data.get('method', 'GET')
        inputs = form_data.get('inputs', [])
        
        for input_field in inputs:
            input_name = input_field.get('name', '')
            if not input_name:
                continue
            
            input_type = input_field.get('type', 'text')
            if input_type in ['hidden', 'submit', 'button', 'file', 'password']:
                continue
            
            for payload in self.PAYLOADS[:5]:
                # Build form data
                data = {}
                for inp in inputs:
                    if inp['name'] == input_name:
                        data[inp['name']] = payload
                    else:
                        data[inp['name']] = inp.get('value', 'test')
                
                try:
                    if method == 'POST':
                        async with session.post(
                            action_url,
                            data=data,
                            timeout=aiohttp.ClientTimeout(total=10),
                            ssl=False
                        ) as response:
                            text = await response.text()
                    else:
                        async with session.get(
                            action_url,
                            params=data,
                            timeout=aiohttp.ClientTimeout(total=10),
                            ssl=False
                        ) as response:
                            text = await response.text()
                    
                    # Check if payload is reflected
                    if payload in text:
                        vulnerabilities.append(self.create_vulnerability(
                            name="Reflected XSS (Form)",
                            severity="high",
                            url=action_url,
                            description=f"폼 필드 '{input_name}'에서 Reflected XSS 취약점이 발견되었습니다. "
                                       f"공격자가 악성 스크립트를 삽입하여 사용자의 세션을 탈취하거나 "
                                       f"피싱 공격을 수행할 수 있습니다.",
                            evidence=f"Payload reflected in response:\n{payload}",
                            parameter=input_name,
                            method=method,
                            recommendation="1. 출력 시 HTML 엔티티 인코딩을 적용하세요.\n"
                                          "2. Content-Security-Policy 헤더를 설정하세요.\n"
                                          "3. HttpOnly 플래그로 쿠키를 보호하세요.\n"
                                          "4. 입력값 검증 및 필터링을 수행하세요.",
                            references=[
                                "https://owasp.org/www-community/attacks/xss/",
                                "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
                            ],
                            cwe_id="CWE-79",
                            cvss_score=7
                        ))
                        return vulnerabilities
                        
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _test_reflected_xss(
        self,
        session: aiohttp.ClientSession,
        url: str,
        param: str
    ) -> List[Dict[str, Any]]:
        """
        Test for reflected XSS in a URL parameter
        """
        vulnerabilities = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        for payload in self.PAYLOADS[:6]:
            test_url = f"{base_url}?{param}={payload}"
            
            try:
                async with session.get(
                    test_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False,
                    allow_redirects=True
                ) as response:
                    text = await response.text()
                    
                    # Check if payload is reflected unencoded
                    if payload in text:
                        # Verify it's in a dangerous context
                        dangerous_patterns = [
                            f'<script>{payload}',
                            f'onerror="{payload}"',
                            f"onerror='{payload}'",
                            payload,  # Direct reflection
                        ]
                        
                        for pattern in dangerous_patterns:
                            if pattern in text:
                                vulnerabilities.append(self.create_vulnerability(
                                    name="Reflected XSS",
                                    severity="high",
                                    url=url,
                                    description=f"파라미터 '{param}'에서 Reflected XSS 취약점이 발견되었습니다. "
                                               f"악성 JavaScript 코드가 페이지에 삽입되어 실행될 수 있습니다. "
                                               f"이를 통해 세션 하이재킹, 피싱, 악성코드 유포 등의 공격이 가능합니다.",
                                    evidence=f"Payload: {payload}\nReflected in response without encoding",
                                    parameter=param,
                                    method="GET",
                                    recommendation="1. 모든 사용자 입력을 출력 시 HTML 인코딩하세요.\n"
                                                  "2. Content-Security-Policy 헤더를 구현하세요.\n"
                                                  "3. X-XSS-Protection 헤더를 설정하세요.\n"
                                                  "4. 템플릿 엔진의 자동 이스케이프 기능을 사용하세요.",
                                    references=[
                                        "https://owasp.org/www-community/attacks/xss/",
                                        "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
                                    ],
                                    cwe_id="CWE-79",
                                    cvss_score=7
                                ))
                                return vulnerabilities
                                
            except Exception:
                continue
        
        return vulnerabilities

