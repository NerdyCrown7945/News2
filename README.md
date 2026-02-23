# ai-scitech-news-digest

AI/과학기술 뉴스 수집·요약·번역·검색 시스템입니다.

## 구조
- `backend/`: FastAPI + SQLite (Postgres로 전환 가능)
- `frontend/`: Next.js App Router UI
- `backend/tools/generate_static_data.py`: GitHub Pages fallback용 정적 JSON 생성
- `frontend/public/data/`: fallback 데이터 (`feed.json`, `articles/*.json`)

## 핵심 정책
- **원문 링크 정책(매우 중요)**
  - RSS에서 근거 있는 URL만 사용: `entry.link -> links[rel=alternate] -> guid/id(URL)`
  - `utm_*` 등 추적 파라미터만 제거, path는 유지
  - 홈/섹션 경로(`/blog`, `/news`, `/research`, `/press`, `/updates`, `/discover/blog`)는 기사 링크로 인정하지 않음
  - 위 조건이면 `url=""` 저장 + UI에서 “원문 링크 없음” 안내
  - 제목 기반 URL 추측 생성 금지

## 로컬 실행 (Windows PowerShell 기준)

### 1) 백엔드 실행
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH='.'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) 수집 실행
```powershell
cd backend
$env:PYTHONPATH='.'
python -c "from app.ingest import ingest_from_sources; print(ingest_from_sources())"
```

### 3) 프론트 실행
```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_BASE='http://127.0.0.1:8000'
npm run dev
```
브라우저: `http://127.0.0.1:3000/news`

## Pages 모드 (정적 fallback)
- `NEXT_PUBLIC_STATIC_ONLY=true` 로 빌드하면 API 없이도 `public/data` 기반으로 화면 표시
- `.github/workflows/update-news-data.yml`이 정적 데이터 자동 갱신

## API
- `GET /health`
- `POST /ingest/run`
- `GET /feed?topic=ai|scitech|all&range=24h|7d|30d&query=...&sort=new`
- `GET /article/{id}`
- `GET /search?query=...&from=YYYY-MM-DD&to=YYYY-MM-DD&topic=...&tag=...`

## 개발 편의
- `make backend-dev`
- `make ingest`
- `make frontend-dev`
- `docker-compose up`

## 환경 변수
- `DATABASE_URL` (예: `sqlite:///./news.db` 또는 `postgresql+psycopg://news:news@localhost:5432/news`)
- `OPENAI_API_KEY` (있으면 자연스러운 한국어 요약/번역 LLM 사용)
- `NEXT_PUBLIC_API_BASE` (프론트에서 API 주소)
- `NEXT_PUBLIC_STATIC_ONLY=true` (정적 fallback 강제)
