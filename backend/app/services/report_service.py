"""
Report generation service
"""
import io
from datetime import datetime
from typing import List
from jinja2 import Template

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability, Severity


# HTML Report Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureScan 보안 점검 보고서</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: #e0e0e0;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            padding: 40px;
            background: linear-gradient(135deg, rgba(0, 212, 170, 0.1) 0%, rgba(0, 150, 136, 0.05) 100%);
            border-radius: 20px;
            border: 1px solid rgba(0, 212, 170, 0.2);
        }
        
        .logo {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00D4AA 0%, #00BCD4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #888;
            font-size: 1.1rem;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        .summary-number {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .summary-label {
            color: #888;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .critical .summary-number { color: #FF4757; }
        .high .summary-number { color: #FF6B35; }
        .medium .summary-number { color: #FFA502; }
        .low .summary-number { color: #2ED573; }
        .info .summary-number { color: #00D4AA; }
        
        .section {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .section-title::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(135deg, #00D4AA 0%, #00BCD4 100%);
            border-radius: 2px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        
        .info-item {
            padding: 16px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
        }
        
        .info-label {
            color: #888;
            font-size: 0.85rem;
            margin-bottom: 4px;
        }
        
        .info-value {
            color: #fff;
            font-size: 1rem;
            word-break: break-all;
        }
        
        .vuln-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .vuln-card {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 16px;
            padding: 24px;
            border-left: 4px solid;
        }
        
        .vuln-card.critical { border-color: #FF4757; }
        .vuln-card.high { border-color: #FF6B35; }
        .vuln-card.medium { border-color: #FFA502; }
        .vuln-card.low { border-color: #2ED573; }
        .vuln-card.info { border-color: #00D4AA; }
        
        .vuln-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }
        
        .vuln-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #fff;
        }
        
        .severity-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .severity-badge.critical { background: rgba(255, 71, 87, 0.2); color: #FF4757; }
        .severity-badge.high { background: rgba(255, 107, 53, 0.2); color: #FF6B35; }
        .severity-badge.medium { background: rgba(255, 165, 2, 0.2); color: #FFA502; }
        .severity-badge.low { background: rgba(46, 213, 115, 0.2); color: #2ED573; }
        .severity-badge.info { background: rgba(0, 212, 170, 0.2); color: #00D4AA; }
        
        .vuln-url {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #00D4AA;
            margin-bottom: 12px;
            padding: 10px 14px;
            background: rgba(0, 212, 170, 0.1);
            border-radius: 8px;
            word-break: break-all;
        }
        
        .vuln-description {
            color: #ccc;
            margin-bottom: 16px;
        }
        
        .vuln-section {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .vuln-section-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #888;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .evidence-box {
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            padding: 16px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 8px;
            overflow-x: auto;
            color: #e0e0e0;
        }
        
        .recommendation {
            color: #2ED573;
            line-height: 1.8;
        }
        
        .footer {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #00D4AA;
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .vuln-header {
                flex-direction: column;
                gap: 12px;
            }
        }
        
        @media print {
            body {
                background: white;
                color: #333;
            }
            
            .summary-card, .section, .vuln-card {
                background: #f5f5f5;
                border-color: #ddd;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">🛡️ SecureScan</div>
            <p class="subtitle">웹 보안 취약점 점검 보고서</p>
        </header>
        
        <div class="summary-grid">
            <div class="summary-card critical">
                <div class="summary-number">{{ scan.critical_count }}</div>
                <div class="summary-label">Critical</div>
            </div>
            <div class="summary-card high">
                <div class="summary-number">{{ scan.high_count }}</div>
                <div class="summary-label">High</div>
            </div>
            <div class="summary-card medium">
                <div class="summary-number">{{ scan.medium_count }}</div>
                <div class="summary-label">Medium</div>
            </div>
            <div class="summary-card low">
                <div class="summary-number">{{ scan.low_count }}</div>
                <div class="summary-label">Low</div>
            </div>
            <div class="summary-card info">
                <div class="summary-number">{{ scan.info_count }}</div>
                <div class="summary-label">Info</div>
            </div>
        </div>
        
        <section class="section">
            <h2 class="section-title">스캔 정보</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">대상 URL</div>
                    <div class="info-value">{{ scan.target_url }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">도메인</div>
                    <div class="info-value">{{ scan.target_domain }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">스캔 유형</div>
                    <div class="info-value">{{ scan.scan_type }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">스캔 깊이</div>
                    <div class="info-value">{{ scan.scan_depth }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">시작 시간</div>
                    <div class="info-value">{{ scan.started_at }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">완료 시간</div>
                    <div class="info-value">{{ scan.completed_at }}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2 class="section-title">발견된 취약점 ({{ vulnerabilities|length }}건)</h2>
            <div class="vuln-list">
                {% for vuln in vulnerabilities %}
                <div class="vuln-card {{ vuln.severity.value }}">
                    <div class="vuln-header">
                        <h3 class="vuln-title">{{ vuln.name }}</h3>
                        <span class="severity-badge {{ vuln.severity.value }}">{{ vuln.severity.value }}</span>
                    </div>
                    <div class="vuln-url">{{ vuln.affected_url }}</div>
                    <p class="vuln-description">{{ vuln.description }}</p>
                    
                    {% if vuln.evidence %}
                    <div class="vuln-section">
                        <div class="vuln-section-title">증거</div>
                        <div class="evidence-box">{{ vuln.evidence }}</div>
                    </div>
                    {% endif %}
                    
                    {% if vuln.recommendation %}
                    <div class="vuln-section">
                        <div class="vuln-section-title">권장 조치</div>
                        <p class="recommendation">{{ vuln.recommendation }}</p>
                    </div>
                    {% endif %}
                    
                    {% if vuln.cwe_id %}
                    <div class="vuln-section">
                        <div class="vuln-section-title">참조</div>
                        <p>CWE: {{ vuln.cwe_id }}</p>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </section>
        
        <footer class="footer">
            <p>이 보고서는 <a href="#">SecureScan</a>에 의해 자동 생성되었습니다.</p>
            <p>생성일: {{ generated_at }}</p>
        </footer>
    </div>
</body>
</html>
"""


async def generate_html_report(scan: Scan, vulnerabilities: List[Vulnerability]) -> str:
    """Generate HTML report"""
    template = Template(HTML_TEMPLATE)
    
    html_content = template.render(
        scan=scan,
        vulnerabilities=vulnerabilities,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    
    return html_content


def sanitize_text_for_pdf(text) -> str:
    """Remove or replace non-ASCII characters for PDF compatibility"""
    if text is None:
        return ""
    text = str(text)
    if not text:
        return ""
    
    # 한글 -> 영어 매핑 (일반적인 보안 용어)
    replacements = {
        '취약점': 'Vulnerability',
        '권장': 'Recommended',
        '조치': 'Action',
        '설명': 'Description',
        '증거': 'Evidence',
        '참조': 'Reference',
        '심각': 'Critical',
        '높음': 'High',
        '중간': 'Medium',
        '낮음': 'Low',
        '정보': 'Info',
        '스캔': 'Scan',
        '완료': 'Completed',
        '실패': 'Failed',
        '진행': 'Running',
        '대기': 'Pending',
        '파라미터': 'Parameter',
        '에서': 'in',
        '발견': 'found',
        '공격자': 'Attacker',
        '사용자': 'User',
        '입력': 'Input',
        '출력': 'Output',
        '서버': 'Server',
        '클라이언트': 'Client',
        '데이터': 'Data',
        '보안': 'Security',
        '헤더': 'Header',
        '쿠키': 'Cookie',
        '토큰': 'Token',
        '인증': 'Authentication',
        '권한': 'Authorization',
        '세션': 'Session',
        '비밀번호': 'Password',
        '암호화': 'Encryption',
        '복호화': 'Decryption',
        '해시': 'Hash',
        '솔트': 'Salt',
        '키': 'Key',
        '값': 'Value',
        '요청': 'Request',
        '응답': 'Response',
        '이메일': 'Email',
        '파일': 'File',
        '경로': 'Path',
        '디렉토리': 'Directory',
        '폴더': 'Folder',
        '업로드': 'Upload',
        '다운로드': 'Download',
        '실행': 'Execute',
        '삭제': 'Delete',
        '수정': 'Modify',
        '생성': 'Create',
        '읽기': 'Read',
        '쓰기': 'Write',
        '접근': 'Access',
        '차단': 'Block',
        '허용': 'Allow',
        '거부': 'Deny',
        '사용': 'Use',
        '설정': 'Setting',
        '옵션': 'Option',
        '기본': 'Default',
        '최소': 'Minimum',
        '최대': 'Maximum',
        '필수': 'Required',
        '선택': 'Optional',
        '오류': 'Error',
        '경고': 'Warning',
        '주의': 'Caution',
        '위험': 'Danger',
        '안전': 'Safe',
        '검증': 'Validation',
        '확인': 'Verify',
        '테스트': 'Test',
        '검사': 'Check',
        '분석': 'Analysis',
        '결과': 'Result',
        '보고서': 'Report',
        '통계': 'Statistics',
        '요약': 'Summary',
        '상세': 'Detail',
        '목록': 'List',
        '항목': 'Item',
        '페이지': 'Page',
        '사이트': 'Site',
        '웹': 'Web',
        '앱': 'App',
        '응용': 'Application',
        '프로그램': 'Program',
        '시스템': 'System',
        '네트워크': 'Network',
        '프로토콜': 'Protocol',
        '포트': 'Port',
        '호스트': 'Host',
        '도메인': 'Domain',
        '주소': 'Address',
        '연결': 'Connection',
        '종료': 'Terminate',
        '시작': 'Start',
        '중지': 'Stop',
        '재시작': 'Restart',
        '로그': 'Log',
        '기록': 'Record',
        '이력': 'History',
        '날짜': 'Date',
        '시간': 'Time',
        '타임아웃': 'Timeout',
        '지연': 'Delay',
        '대기': 'Wait',
        '완료됨': 'Completed',
        '없습니다': 'not found',
        '있습니다': 'exists',
        '합니다': '',
        '입니다': '',
        '됩니다': '',
        '하세요': '',
        '니다': '',
    }
    result = text
    for kr, en in replacements.items():
        result = result.replace(kr, en)
    
    # 남은 비-ASCII 문자 제거 (공백으로 대체)
    cleaned = []
    for char in result:
        if ord(char) < 128:
            cleaned.append(char)
        else:
            cleaned.append(' ')
    
    # 연속된 공백 제거
    result = ''.join(cleaned)
    while '  ' in result:
        result = result.replace('  ', ' ')
    
    return result.strip()


async def generate_pdf_report(scan: Scan, vulnerabilities: List[Vulnerability]) -> io.BytesIO:
    """Generate PDF report using fpdf2 with Korean support"""
    try:
        from fpdf import FPDF
    except ImportError:
        raise Exception("fpdf2가 설치되지 않았습니다. 'pip install fpdf2'를 실행해주세요.")
    
    import os
    
    # 심각도 색상 (RGB)
    severity_colors = {
        'critical': (255, 71, 87),
        'high': (255, 107, 53),
        'medium': (255, 165, 2),
        'low': (46, 213, 115),
        'info': (0, 212, 170),
    }
    
    # 심각도 한글 매핑
    severity_korean = {
        'critical': '심각',
        'high': '높음',
        'medium': '중간',
        'low': '낮음',
        'info': '정보',
    }
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 한글 폰트 경로 (Windows / Linux)
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",  # Windows
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux (Ubuntu)
        "/usr/share/fonts/nanum/NanumGothic.ttf",  # Linux (Other)
    ]
    font_bold_paths = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/nanum/NanumGothicBold.ttf",
    ]
    
    font_name = "Helvetica"  # 기본값
    use_korean = False
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            pdf.add_font("Korean", "", font_path)
            # Bold 폰트도 찾기
            for bold_path in font_bold_paths:
                if os.path.exists(bold_path):
                    pdf.add_font("Korean", "B", bold_path)
                    break
            else:
                pdf.add_font("Korean", "B", font_path)
            font_name = "Korean"
            use_korean = True
            break
    
    pdf.add_page()
    
    # 텍스트 선택 (한글 폰트 있으면 한글, 없으면 영어)
    if use_korean:
        txt_title = 'SecureScan 보안 보고서'
        txt_subtitle = '웹 취약점 분석 보고서'
        txt_scan_summary = '스캔 요약'
        txt_target_url = '대상 URL:'
        txt_domain = '도메인:'
        txt_scan_type = '스캔 유형:'
        txt_status = '상태:'
        txt_depth = '깊이'
        txt_vuln_stats = '취약점 통계'
        status_map = {'completed': '완료', 'running': '진행 중', 'pending': '대기 중', 'failed': '실패'}
        stats_labels = ['심각 (Critical)', '높음 (High)', '중간 (Medium)', '낮음 (Low)', '정보 (Info)']
    else:
        txt_title = 'SecureScan Security Report'
        txt_subtitle = 'Web Vulnerability Assessment Report'
        txt_scan_summary = 'Scan Summary'
        txt_target_url = 'Target URL:'
        txt_domain = 'Domain:'
        txt_scan_type = 'Scan Type:'
        txt_status = 'Status:'
        txt_depth = 'depth'
        txt_vuln_stats = 'Vulnerability Statistics'
        status_map = {'completed': 'Completed', 'running': 'Running', 'pending': 'Pending', 'failed': 'Failed'}
        stats_labels = ['Critical', 'High', 'Medium', 'Low', 'Info']
    
    # 헤더
    pdf.set_font(font_name, 'B', 22)
    pdf.set_text_color(0, 212, 170)
    pdf.cell(0, 15, txt_title, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font(font_name, '', 11)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 8, txt_subtitle, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)
    
    # 스캔 요약
    pdf.set_font(font_name, 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(30, 30, 46)
    pdf.cell(0, 12, txt_scan_summary, fill=True, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    
    # 안전하게 값 변환
    target_url = str(scan.target_url)[:80] if scan.target_url else "N/A"
    target_domain = str(scan.target_domain) if scan.target_domain else "N/A"
    scan_type = str(scan.scan_type) if scan.scan_type else "N/A"
    scan_status = scan.status.value if hasattr(scan.status, 'value') else str(scan.status)
    scan_status_display = status_map.get(scan_status, scan_status)
    
    pdf.set_font(font_name, '', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(50, 8, txt_target_url, new_x='RIGHT')
    pdf.cell(0, 8, target_url, new_x='LMARGIN', new_y='NEXT')
    pdf.cell(50, 8, txt_domain, new_x='RIGHT')
    pdf.cell(0, 8, target_domain, new_x='LMARGIN', new_y='NEXT')
    pdf.cell(50, 8, txt_scan_type, new_x='RIGHT')
    pdf.cell(0, 8, f'{scan_type} ({txt_depth}: {scan.scan_depth})', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(50, 8, txt_status, new_x='RIGHT')
    pdf.cell(0, 8, scan_status_display, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)
    
    # 취약점 통계
    pdf.set_font(font_name, 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(30, 30, 46)
    pdf.cell(0, 12, txt_vuln_stats, fill=True, new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    
    stats = [
        (stats_labels[0], scan.critical_count, severity_colors['critical']),
        (stats_labels[1], scan.high_count, severity_colors['high']),
        (stats_labels[2], scan.medium_count, severity_colors['medium']),
        (stats_labels[3], scan.low_count, severity_colors['low']),
        (stats_labels[4], scan.info_count, severity_colors['info']),
    ]
    
    pdf.set_font(font_name, 'B', 11)
    for label, count, color in stats:
        pdf.set_text_color(*color)
        pdf.cell(50, 8, f'{label}:', new_x='RIGHT')
        pdf.cell(20, 8, str(count), new_x='LMARGIN', new_y='NEXT')
    
    pdf.ln(5)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font(font_name, 'B', 12)
    txt_total = '총 취약점 수' if use_korean else 'Total Vulnerabilities'
    pdf.cell(0, 10, f'{txt_total}: {scan.total_vulnerabilities}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)
    
    # 텍스트 설정
    if use_korean:
        txt_vuln_detail = '취약점 상세 정보'
        txt_unknown = '알 수 없음'
        txt_no_desc = '설명 없음'
        txt_desc = '설명'
        txt_recommendation = '권장 조치'
        txt_reference = '참조'
        txt_generated = '보고서 생성일'
        txt_scanner = 'SecureScan - 웹 보안 스캐너'
    else:
        txt_vuln_detail = 'Vulnerability Details'
        txt_unknown = 'Unknown'
        txt_no_desc = 'No description'
        txt_desc = 'Description'
        txt_recommendation = 'Recommendation'
        txt_reference = 'Reference'
        txt_generated = 'Report Generated'
        txt_scanner = 'SecureScan - Web Security Scanner'
    
    # 취약점 상세
    if vulnerabilities:
        pdf.set_font(font_name, 'B', 14)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(30, 30, 46)
        pdf.cell(0, 12, txt_vuln_detail, fill=True, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(5)
        
        for i, vuln in enumerate(vulnerabilities, 1):
            # 새 페이지 필요시 추가
            if pdf.get_y() > 240:
                pdf.add_page()
            
            # 안전하게 severity 값 추출
            severity = vuln.severity.value if hasattr(vuln.severity, 'value') else str(vuln.severity)
            color = severity_colors.get(severity, (128, 128, 128))
            severity_display = severity_korean.get(severity, severity) if use_korean else severity.upper()
            
            # 안전하게 값 변환
            vuln_name = str(vuln.name) if vuln.name else txt_unknown
            if not use_korean:
                vuln_name = sanitize_text_for_pdf(vuln_name)
            affected_url = str(vuln.affected_url) if vuln.affected_url else "N/A"
            description = str(vuln.description) if vuln.description else txt_no_desc
            if not use_korean:
                description = sanitize_text_for_pdf(description)
            
            # 취약점 제목
            pdf.set_font(font_name, 'B', 11)
            pdf.set_text_color(*color)
            pdf.cell(0, 8, f'{i}. [{severity_display}] {vuln_name}', new_x='LMARGIN', new_y='NEXT')
            
            # URL
            pdf.set_font(font_name, '', 9)
            pdf.set_text_color(0, 150, 136)
            url_display = affected_url[:100] + '...' if len(affected_url) > 100 else affected_url
            pdf.cell(0, 6, f'URL: {url_display}', new_x='LMARGIN', new_y='NEXT')
            
            # 설명
            pdf.set_text_color(80, 80, 80)
            pdf.set_font(font_name, '', 10)
            desc_display = description[:300] + '...' if len(description) > 300 else description
            if desc_display.strip():
                pdf.set_x(10)
                pdf.multi_cell(190, 5, f'{txt_desc}: {desc_display}')
            
            # 권장 조치
            if vuln.recommendation:
                recommendation = str(vuln.recommendation)[:200]
                if not use_korean:
                    recommendation = sanitize_text_for_pdf(recommendation)
                if recommendation.strip():
                    pdf.set_text_color(46, 213, 115)
                    pdf.set_font(font_name, '', 9)
                    if len(str(vuln.recommendation)) > 200:
                        recommendation += '...'
                    pdf.set_x(10)
                    pdf.multi_cell(190, 5, f'{txt_recommendation}: {recommendation}')
            
            # CWE
            if vuln.cwe_id:
                pdf.set_text_color(128, 128, 128)
                pdf.set_font(font_name, '', 9)
                pdf.cell(0, 5, f'{txt_reference}: {vuln.cwe_id}', new_x='LMARGIN', new_y='NEXT')
            
            pdf.ln(5)
    
    # 푸터 정보
    pdf.ln(10)
    pdf.set_font(font_name, '', 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, f'{txt_generated}: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, txt_scanner, align='C')
    
    # PDF 출력
    pdf_buffer = io.BytesIO()
    pdf_buffer.write(pdf.output())
    pdf_buffer.seek(0)
    return pdf_buffer

