"""
Security Headers vulnerability checker
"""
from typing import List, Dict, Any
import aiohttp

from app.scanner.checks.base import BaseChecker


class SecurityHeadersChecker(BaseChecker):
    """
    Check for missing or misconfigured security headers
    """
    
    vuln_type = "security_headers"
    
    # Security headers to check
    SECURITY_HEADERS = {
        'Strict-Transport-Security': {
            'severity': 'medium',
            'description': 'HSTS 헤더가 설정되지 않았습니다. 이 헤더는 브라우저가 HTTPS 연결만 사용하도록 강제합니다.',
            'recommendation': 'Strict-Transport-Security: max-age=31536000; includeSubDomains 헤더를 추가하세요.',
            'cwe_id': 'CWE-319'
        },
        'X-Content-Type-Options': {
            'severity': 'low',
            'description': 'X-Content-Type-Options 헤더가 설정되지 않았습니다. MIME 타입 스니핑 공격에 취약할 수 있습니다.',
            'recommendation': 'X-Content-Type-Options: nosniff 헤더를 추가하세요.',
            'cwe_id': 'CWE-16'
        },
        'X-Frame-Options': {
            'severity': 'medium',
            'description': 'X-Frame-Options 헤더가 설정되지 않았습니다. Clickjacking 공격에 취약할 수 있습니다.',
            'recommendation': 'X-Frame-Options: DENY 또는 SAMEORIGIN 헤더를 추가하세요.',
            'cwe_id': 'CWE-1021'
        },
        'Content-Security-Policy': {
            'severity': 'medium',
            'description': 'Content-Security-Policy 헤더가 설정되지 않았습니다. XSS 및 데이터 인젝션 공격 방어가 약화됩니다.',
            'recommendation': "Content-Security-Policy: default-src 'self' 등 적절한 정책을 설정하세요.",
            'cwe_id': 'CWE-16'
        },
        'X-XSS-Protection': {
            'severity': 'low',
            'description': 'X-XSS-Protection 헤더가 설정되지 않았습니다. 브라우저의 XSS 필터를 활성화하세요.',
            'recommendation': 'X-XSS-Protection: 1; mode=block 헤더를 추가하세요.',
            'cwe_id': 'CWE-79'
        },
        'Referrer-Policy': {
            'severity': 'info',
            'description': 'Referrer-Policy 헤더가 설정되지 않았습니다. 민감한 URL 정보가 다른 사이트로 유출될 수 있습니다.',
            'recommendation': 'Referrer-Policy: strict-origin-when-cross-origin 헤더를 추가하세요.',
            'cwe_id': 'CWE-200'
        },
        'Permissions-Policy': {
            'severity': 'info',
            'description': 'Permissions-Policy 헤더가 설정되지 않았습니다. 브라우저 기능 사용을 제한할 수 없습니다.',
            'recommendation': 'Permissions-Policy 헤더로 불필요한 브라우저 기능을 비활성화하세요.',
            'cwe_id': 'CWE-16'
        }
    }
    
    # Insecure header configurations
    INSECURE_CONFIGS = {
        'X-Powered-By': {
            'severity': 'info',
            'description': 'X-Powered-By 헤더가 서버 기술 정보를 노출하고 있습니다.',
            'recommendation': '서버 설정에서 X-Powered-By 헤더를 제거하세요.'
        },
        'Server': {
            'severity': 'info',
            'description': 'Server 헤더가 서버 소프트웨어 정보를 노출하고 있습니다.',
            'recommendation': 'Server 헤더의 상세 정보를 숨기거나 제거하세요.',
            'check_value': True
        }
    }
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for security header issues
        """
        vulnerabilities = []
        
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False,
                allow_redirects=True
            ) as response:
                headers = response.headers
                
                # Check for missing security headers
                for header_name, header_info in self.SECURITY_HEADERS.items():
                    if header_name not in headers:
                        vulnerabilities.append(self.create_vulnerability(
                            name=f"Missing Security Header: {header_name}",
                            severity=header_info['severity'],
                            url=url,
                            description=header_info['description'],
                            evidence=f"응답에 {header_name} 헤더가 포함되어 있지 않습니다.",
                            recommendation=header_info['recommendation'],
                            references=[
                                "https://owasp.org/www-project-secure-headers/",
                                f"https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/{header_name}"
                            ],
                            cwe_id=header_info.get('cwe_id')
                        ))
                    else:
                        # Check for weak configurations
                        await self._check_header_value(
                            url, header_name, headers[header_name], vulnerabilities
                        )
                
                # Check for information disclosure headers
                for header_name, header_info in self.INSECURE_CONFIGS.items():
                    if header_name in headers:
                        header_value = headers[header_name]
                        
                        # For Server header, check if it reveals detailed info
                        if header_info.get('check_value'):
                            if any(x in header_value.lower() for x in 
                                   ['apache', 'nginx', 'iis', 'php', 'asp', 'tomcat']):
                                vulnerabilities.append(self.create_vulnerability(
                                    name=f"Information Disclosure: {header_name}",
                                    severity=header_info['severity'],
                                    url=url,
                                    description=header_info['description'],
                                    evidence=f"{header_name}: {header_value}",
                                    recommendation=header_info['recommendation'],
                                    references=[
                                        "https://owasp.org/www-project-web-security-testing-guide/"
                                    ],
                                    cwe_id="CWE-200"
                                ))
                        else:
                            vulnerabilities.append(self.create_vulnerability(
                                name=f"Information Disclosure: {header_name}",
                                severity=header_info['severity'],
                                url=url,
                                description=header_info['description'],
                                evidence=f"{header_name}: {header_value}",
                                recommendation=header_info['recommendation'],
                                references=[
                                    "https://owasp.org/www-project-web-security-testing-guide/"
                                ],
                                cwe_id="CWE-200"
                            ))
                
                # Check for insecure cookies
                await self._check_cookies(url, response, vulnerabilities)
                
        except Exception:
            pass
        
        return vulnerabilities
    
    async def _check_header_value(
        self,
        url: str,
        header_name: str,
        header_value: str,
        vulnerabilities: List[Dict[str, Any]]
    ):
        """
        Check if a security header has a weak configuration
        """
        header_lower = header_value.lower()
        
        if header_name == 'Strict-Transport-Security':
            # Check for short max-age
            if 'max-age=' in header_lower:
                try:
                    max_age = int(header_lower.split('max-age=')[1].split(';')[0])
                    if max_age < 31536000:  # Less than 1 year
                        vulnerabilities.append(self.create_vulnerability(
                            name="Weak HSTS Configuration",
                            severity="low",
                            url=url,
                            description="HSTS max-age 값이 권장값(1년)보다 짧습니다.",
                            evidence=f"Strict-Transport-Security: {header_value}",
                            recommendation="max-age를 최소 31536000(1년) 이상으로 설정하세요.",
                            cwe_id="CWE-319"
                        ))
                except:
                    pass
        
        elif header_name == 'Content-Security-Policy':
            # Check for unsafe directives
            if "'unsafe-inline'" in header_lower or "'unsafe-eval'" in header_lower:
                vulnerabilities.append(self.create_vulnerability(
                    name="Weak CSP Configuration",
                    severity="medium",
                    url=url,
                    description="CSP에 unsafe-inline 또는 unsafe-eval이 포함되어 있어 XSS 방어 효과가 감소합니다.",
                    evidence=f"Content-Security-Policy: {header_value}",
                    recommendation="가능하면 unsafe-inline과 unsafe-eval을 제거하고 nonce 또는 hash를 사용하세요.",
                    cwe_id="CWE-79"
                ))
    
    async def _check_cookies(
        self,
        url: str,
        response: aiohttp.ClientResponse,
        vulnerabilities: List[Dict[str, Any]]
    ):
        """
        Check for insecure cookie configurations
        """
        cookies = response.cookies
        
        for cookie_name, cookie in cookies.items():
            issues = []
            
            # Check for missing Secure flag (on HTTPS)
            if url.startswith('https://') and not cookie.get('secure'):
                issues.append("Secure 플래그 없음")
            
            # Check for missing HttpOnly flag
            if not cookie.get('httponly'):
                issues.append("HttpOnly 플래그 없음")
            
            # Check for missing SameSite
            samesite = cookie.get('samesite', '').lower()
            if not samesite or samesite == 'none':
                issues.append("SameSite 속성 미설정 또는 None")
            
            if issues:
                vulnerabilities.append(self.create_vulnerability(
                    name=f"Insecure Cookie: {cookie_name}",
                    severity="low" if len(issues) == 1 else "medium",
                    url=url,
                    description=f"쿠키 '{cookie_name}'의 보안 설정이 미흡합니다: {', '.join(issues)}",
                    evidence=f"Cookie: {cookie_name}\nIssues: {', '.join(issues)}",
                    recommendation="모든 쿠키에 Secure, HttpOnly, SameSite=Strict 또는 Lax 속성을 설정하세요.",
                    references=[
                        "https://owasp.org/www-community/controls/SecureCookieAttribute"
                    ],
                    cwe_id="CWE-614"
                ))

