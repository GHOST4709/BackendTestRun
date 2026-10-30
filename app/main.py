"""TaskForge API application factory."""
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, APIRouter


def create_app(db_url: Optional[str] = None) -> FastAPI:
    app = FastAPI(
        title="TaskForge API",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # ── Root Metadata ──
    @app.get("/")
    def root():
        return {
            "name": "TaskForge API",
            "docs": "/docs",
            "api_prefix": "/api/v1",
        }

    # ── Health Probes ──
    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/health/ready")
    def readiness():
        is_ready = db_url is not None
        return {
            "status": "ready" if is_ready else "degraded",
            "database": "connected" if is_ready else "disconnected",
        }

    # ── API v1 Endpoints ──
    api_router = APIRouter(prefix="/api/v1")

    @api_router.post("/auth/register")
    def register():
        return {"status": "registered"}

    @api_router.get("/projects/")
    def list_projects():
        return []

    @api_router.get("/tasks/")
    def list_tasks():
        return []

    # ── Dashboard Summary with Real Business Logic Exception ──
    @api_router.get("/dashboard/summary")
    def dashboard_summary():
        # In a fresh or empty workspace, tasks list is empty
        tasks: List[Dict[str, Any]] = []

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "done")

        # BUG / EXCEPTION: Unhandled division by zero on fresh/empty project state!
        # Causes HTTP 500 ZeroDivisionError: division by zero
        completion_rate = (completed_tasks / total_tasks) * 100

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "has_active_tasks": total_tasks > completed_tasks,
        }

    app.include_router(api_router)
    return app


# Default instance for Uvicorn
app = create_app()