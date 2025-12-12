# 🛡️ SecureScan - 웹 보안 취약점 점검 서비스

<div align="center">

![SecureScan Logo](https://img.shields.io/badge/SecureScan-v1.0.0-00D4AA?style=for-the-badge&logo=security&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**AI 기반 스마트 웹 보안 스캐닝 서비스**

[시작하기](#-시작하기) • [기능](#-주요-기능) • [API 문서](#-api-문서) • [기여하기](#-기여하기)

</div>

---

## 📋 목차

- [소개](#-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [시작하기](#-시작하기)
- [프로젝트 구조](#-프로젝트-구조)
- [API 문서](#-api-문서)
- [보안 고려사항](#-보안-고려사항)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

---

## 🎯 소개

**SecureScan**은 웹사이트의 보안 취약점을 자동으로 탐지하고 분석하는 서비스입니다.

### 타겟 사용자
- 🧑‍💻 **웹 개발자**: 자신의 사이트 보안 점검
- 🏢 **스타트업**: 보안 감사 및 컴플라이언스
- 🔍 **버그 바운티 헌터**: 취약점 탐지 및 리포팅

### 차별점
- 🤖 **AI 기반 스마트 스캐닝**: 취약점 패턴 학습 및 예측
- 🌐 **실시간 위협 인텔리전스**: 최신 CVE 데이터베이스 연동
- 🇰🇷 **한국어 지원**: 국내 웹 환경 최적화
- 📊 **직관적인 대시보드**: 시각적 보안 리포트

---

## ✨ 주요 기능

### 1. 자동 취약점 스캔
| 취약점 유형 | 설명 |
|------------|------|
| **SQL Injection** | 데이터베이스 공격 탐지 |
| **XSS (Cross-Site Scripting)** | 스크립트 삽입 공격 탐지 |
| **CSRF** | 크로스 사이트 요청 위조 탐지 |
| **SSRF** | 서버 측 요청 위조 탐지 |
| **Directory Traversal** | 경로 조작 공격 탐지 |
| **Security Headers** | 보안 헤더 설정 검사 |

### 2. 보고서 생성
- 📄 PDF/HTML 형식 지원
- 📊 취약점 심각도 분류 (Critical, High, Medium, Low)
- 💡 상세 설명 및 해결 방안 제공
- 📈 시각적 통계 및 차트

### 3. API 연동
- 🔗 RESTful API 제공
- 🔄 CI/CD 파이프라인 연동 (GitHub Actions, Jenkins)
- 📡 Webhook 지원

---

## 🛠 기술 스택

### Backend
- **Python 3.11+**
- **FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy** - ORM
- **PostgreSQL** - 메인 데이터베이스
- **Redis** - 캐싱 및 작업 큐
- **Celery** - 비동기 작업 처리

### Frontend
- **React 18+** - UI 라이브러리
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Zustand** - 상태 관리
- **React Query** - 서버 상태 관리
- **Recharts** - 데이터 시각화

### Security Tools
- **OWASP ZAP API** - 취약점 스캐닝
- **BeautifulSoup4** - HTML 파싱
- **aiohttp** - 비동기 HTTP 클라이언트

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 개발 환경
- **GitHub Actions** - CI/CD

---

## 🚀 시작하기

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis

### 설치 방법

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/securescan.git
cd securescan

# 2. 백엔드 설정
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. 데이터베이스 마이그레이션
alembic upgrade head

# 5. 백엔드 서버 실행
uvicorn app.main:app --reload

# 6. 프론트엔드 설정 (새 터미널)
cd frontend
npm install
npm run dev
```

### Docker로 실행

```bash
# 전체 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

---

## 📁 프로젝트 구조

```
SecureScan/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 라우터
│   │   ├── core/           # 핵심 설정
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── services/       # 비즈니스 로직
│   │   ├── scanner/        # 취약점 스캐너
│   │   └── main.py         # 앱 진입점
│   ├── tests/              # 테스트
│   ├── alembic/            # DB 마이그레이션
│   └── requirements.txt
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # 재사용 컴포넌트
│   │   ├── pages/          # 페이지 컴포넌트
│   │   ├── hooks/          # 커스텀 훅
│   │   ├── stores/         # 상태 관리
│   │   ├── services/       # API 서비스
│   │   └── types/          # TypeScript 타입
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 📖 API 문서

서버 실행 후 아래 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 주요 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/v1/auth/register` | 회원가입 |
| `POST` | `/api/v1/auth/login` | 로그인 |
| `POST` | `/api/v1/scans` | 새 스캔 시작 |
| `GET` | `/api/v1/scans/{id}` | 스캔 결과 조회 |
| `GET` | `/api/v1/scans/{id}/report` | 보고서 다운로드 |
| `GET` | `/api/v1/vulnerabilities` | 취약점 목록 |

---

## 🔒 보안 고려사항

### 서비스 보안
- ✅ HTTPS 필수 (TLS 1.3)
- ✅ JWT 기반 인증
- ✅ Rate Limiting
- ✅ Input Validation
- ✅ CORS 설정

### 사용자 데이터 보호
- ✅ 데이터 암호화 (AES-256)
- ✅ GDPR 준수
- ✅ 개인정보보호법 준수

### 법적 고려사항
- ⚠️ **무단 스캔 금지**: 반드시 사용자 동의 필요
- ⚠️ **취약점 제보 책임**: 버그 바운티 프로그램 가이드라인 준수

---

## 🤝 기여하기

기여를 환영합니다! 아래 단계를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 문의

- **이메일**: support@securescan.io
- **이슈**: [GitHub Issues](https://github.com/your-username/securescan/issues)

---

<div align="center">

**"보안은 제품이 아니라 과정입니다. 끊임없이 진화하는 위협에 대응해야 합니다."**
*- 케빈 미트닉*

Made with ❤️ by SecureScan Team

</div>

