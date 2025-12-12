"""
Cross-Site Request Forgery (CSRF) vulnerability checker
"""
from typing import List, Dict, Any
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

from app.scanner.checks.base import BaseChecker


class CSRFChecker(BaseChecker):
    """
    Check for Cross-Site Request Forgery (CSRF) vulnerabilities
    """
    
    vuln_type = "csrf"
    
    # Common CSRF token field names
    TOKEN_NAMES = [
        'csrf', 'csrf_token', 'csrftoken', 'csrfmiddlewaretoken',
        '_token', 'token', 'authenticity_token', '_csrf',
        'xsrf', 'xsrf_token', 'xsrftoken', '_xsrf',
        '__requestverificationtoken', 'antiforgery'
    ]
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for CSRF vulnerabilities
        """
        vulnerabilities = []
        
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as response:
                if response.status != 200:
                    return vulnerabilities
                
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                
                # Find all forms
                forms = soup.find_all('form')
                
                for form in forms:
                    method = form.get('method', 'get').upper()
                    
                    # Only check POST forms (state-changing)
                    if method != 'POST':
                        continue
                    
                    action = form.get('action', url)
                    
                    # Check for CSRF token
                    has_csrf_token = False
                    
                    for input_tag in form.find_all('input'):
                        input_name = (input_tag.get('name') or '').lower()
                        
                        for token_name in self.TOKEN_NAMES:
                            if token_name in input_name:
                                has_csrf_token = True
                                break
                        
                        if has_csrf_token:
                            break
                    
                    if not has_csrf_token:
                        # Check form inputs to identify its purpose
                        inputs = form.find_all(['input', 'textarea', 'select'])
                        input_names = [inp.get('name', '') for inp in inputs]
                        
                        # Determine form purpose
                        form_purpose = self._identify_form_purpose(input_names, action)
                        
                        if form_purpose:
                            vulnerabilities.append(self.create_vulnerability(
                                name="CSRF Protection Missing",
                                severity="medium" if form_purpose == "general" else "high",
                                url=url,
                                description=f"'{action}' 폼에 CSRF 토큰이 없습니다. "
                                           f"공격자가 사용자를 속여 원치 않는 요청을 보내도록 할 수 있습니다. "
                                           f"특히 {form_purpose} 관련 폼이므로 주의가 필요합니다.",
                                evidence=f"Form action: {action}\nMethod: POST\nNo CSRF token found\n"
                                        f"Form inputs: {', '.join(input_names[:5])}",
                                method="POST",
                                recommendation="1. 모든 상태 변경 폼에 CSRF 토큰을 추가하세요.\n"
                                              "2. SameSite 쿠키 속성을 설정하세요.\n"
                                              "3. 프레임워크의 내장 CSRF 보호 기능을 사용하세요.\n"
                                              "4. Double Submit Cookie 패턴을 고려하세요.",
                                references=[
                                    "https://owasp.org/www-community/attacks/csrf",
                                    "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"
                                ],
                                cwe_id="CWE-352",
                                cvss_score=6
                            ))
                
        except Exception:
            pass
        
        return vulnerabilities
    
    async def check_form(
        self,
        session: aiohttp.ClientSession,
        form_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check specific form for CSRF vulnerabilities
        """
        vulnerabilities = []
        
        method = form_data.get('method', 'GET')
        if method != 'POST':
            return vulnerabilities
        
        inputs = form_data.get('inputs', [])
        action = form_data.get('action', '')
        
        # Check for CSRF token
        has_csrf_token = False
        
        for inp in inputs:
            input_name = (inp.get('name') or '').lower()
            for token_name in self.TOKEN_NAMES:
                if token_name in input_name:
                    has_csrf_token = True
                    break
            if has_csrf_token:
                break
        
        if not has_csrf_token:
            input_names = [inp.get('name', '') for inp in inputs]
            form_purpose = self._identify_form_purpose(input_names, action)
            
            if form_purpose:
                vulnerabilities.append(self.create_vulnerability(
                    name="CSRF Protection Missing",
                    severity="medium" if form_purpose == "general" else "high",
                    url=action,
                    description=f"POST 폼에 CSRF 토큰이 없습니다. "
                               f"이 취약점을 이용하면 공격자가 인증된 사용자의 권한으로 "
                               f"원치 않는 동작을 수행하도록 만들 수 있습니다.",
                    evidence=f"Form action: {action}\nMethod: POST\n"
                            f"Form inputs: {', '.join(input_names[:5])}",
                    method="POST",
                    recommendation="1. Anti-CSRF 토큰을 구현하세요.\n"
                                  "2. 서버에서 토큰을 검증하세요.\n"
                                  "3. SameSite=Strict 또는 Lax 쿠키 속성을 사용하세요.",
                    references=[
                        "https://owasp.org/www-community/attacks/csrf"
                    ],
                    cwe_id="CWE-352",
                    cvss_score=6
                ))
        
        return vulnerabilities
    
    def _identify_form_purpose(self, input_names: List[str], action: str) -> str:
        """
        Identify the purpose of a form based on its inputs
        """
        input_str = ' '.join(input_names).lower()
        action_lower = action.lower()
        
        # High-risk forms
        if any(x in input_str or x in action_lower for x in 
               ['password', 'pwd', 'pass', 'email', 'mail']):
            return "계정 관련"
        
        if any(x in input_str or x in action_lower for x in 
               ['delete', 'remove', 'drop']):
            return "삭제 작업"
        
        if any(x in input_str or x in action_lower for x in 
               ['admin', 'config', 'setting', 'role', 'permission']):
            return "관리자 기능"
        
        if any(x in input_str or x in action_lower for x in 
               ['payment', 'pay', 'card', 'bank', 'transfer', 'money']):
            return "결제/금융"
        
        if any(x in input_str or x in action_lower for x in 
               ['upload', 'file']):
            return "파일 업로드"
        
        # Medium-risk forms
        if any(x in input_str or x in action_lower for x in 
               ['comment', 'post', 'message', 'submit']):
            return "general"
        
        return "general"

