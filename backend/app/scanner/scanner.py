"""
Main security scanner class
"""
import asyncio
from typing import List, Dict, Any, Callable, Optional
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup

from app.scanner.checks.sqli import SQLInjectionChecker
from app.scanner.checks.xss import XSSChecker
from app.scanner.checks.csrf import CSRFChecker
from app.scanner.checks.headers import SecurityHeadersChecker
from app.scanner.checks.ssrf import SSRFChecker
from app.scanner.checks.lfi import LFIChecker


class SecurityScanner:
    """
    Main security scanner that orchestrates all vulnerability checks
    """
    
    def __init__(self, target_url: str, max_depth: int = 3):
        self.target_url = target_url
        self.max_depth = max_depth
        self.visited_urls = set()
        self.found_urls = set()
        self.found_forms = []
        self.vulnerabilities = []
        
        # Initialize checkers
        self.checkers = [
            SQLInjectionChecker(),
            XSSChecker(),
            CSRFChecker(),
            SecurityHeadersChecker(),
            SSRFChecker(),
            LFIChecker(),
        ]
    
    async def run_full_scan(
        self,
        progress_callback: Optional[Callable[[int], Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run a complete security scan
        """
        self.vulnerabilities = []
        
        try:
            # Phase 1: Crawl the website (20%)
            if progress_callback:
                await progress_callback(5)
            
            await self._crawl(self.target_url, depth=0)
            
            if progress_callback:
                await progress_callback(20)
            
            # Phase 2: Run security checks (80%)
            total_checks = len(self.checkers)
            base_progress = 20
            progress_per_check = 70 // total_checks
            
            async with aiohttp.ClientSession() as session:
                for i, checker in enumerate(self.checkers):
                    try:
                        # Run checks on main URL
                        results = await checker.check(session, self.target_url)
                        self.vulnerabilities.extend(results)
                        
                        # Run checks on discovered URLs
                        for url in list(self.found_urls)[:10]:  # Limit to 10 URLs
                            try:
                                results = await checker.check(session, url)
                                self.vulnerabilities.extend(results)
                            except Exception:
                                continue
                        
                        # Run form checks
                        for form in self.found_forms[:5]:  # Limit to 5 forms
                            try:
                                results = await checker.check_form(session, form)
                                self.vulnerabilities.extend(results)
                            except Exception:
                                continue
                        
                    except Exception as e:
                        # Log error but continue with other checks
                        print(f"Error in {checker.__class__.__name__}: {e}")
                    
                    if progress_callback:
                        current_progress = base_progress + (i + 1) * progress_per_check
                        await progress_callback(min(current_progress, 90))
            
            if progress_callback:
                await progress_callback(100)
            
            return self.vulnerabilities
            
        except Exception as e:
            raise Exception(f"스캔 중 오류 발생: {str(e)}")
    
    async def _crawl(self, url: str, depth: int):
        """
        Crawl the website to discover URLs and forms
        """
        if depth > self.max_depth:
            return
        
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10, ssl=False) as response:
                    if response.status != 200:
                        return
                    
                    content_type = response.headers.get('content-type', '')
                    if 'text/html' not in content_type:
                        return
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract links
                    base_domain = urlparse(self.target_url).netloc
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(url, href)
                        parsed = urlparse(full_url)
                        
                        # Only follow same-domain links
                        if parsed.netloc == base_domain:
                            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                            if clean_url not in self.visited_urls:
                                self.found_urls.add(clean_url)
                    
                    # Extract forms
                    for form in soup.find_all('form'):
                        form_data = {
                            'url': url,
                            'action': urljoin(url, form.get('action', '')),
                            'method': form.get('method', 'get').upper(),
                            'inputs': []
                        }
                        
                        for input_tag in form.find_all(['input', 'textarea', 'select']):
                            input_data = {
                                'name': input_tag.get('name', ''),
                                'type': input_tag.get('type', 'text'),
                                'value': input_tag.get('value', '')
                            }
                            if input_data['name']:
                                form_data['inputs'].append(input_data)
                        
                        if form_data['inputs']:
                            self.found_forms.append(form_data)
                    
                    # Recursively crawl discovered URLs
                    tasks = []
                    for found_url in list(self.found_urls)[:5]:  # Limit concurrent crawls
                        if found_url not in self.visited_urls:
                            tasks.append(self._crawl(found_url, depth + 1))
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                        
        except Exception:
            pass  # Silently ignore crawl errors

