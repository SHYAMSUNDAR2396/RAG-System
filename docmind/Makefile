.PHONY: dev dev-backend dev-frontend

dev-backend:
	cd backend && ../../venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	npx -y concurrently "make dev-backend" "make dev-frontend"
