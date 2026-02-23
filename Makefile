backend-dev:
	cd backend && PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

ingest:
	cd backend && PYTHONPATH=. python -c "from app.ingest import ingest_from_sources; print(ingest_from_sources())"

frontend-dev:
	cd frontend && npm install && npm run dev
