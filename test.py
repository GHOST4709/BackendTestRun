"""Root-level pytest smoke & regression tests."""
from fastapi.testclient import TestClient
from app.main import create_app


def test_root_metadata_has_docs_and_api_prefix():
    with TestClient(create_app("sqlite+pysqlite:///:memory:")) as client:
        response = client.get("/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["name"] == "TaskForge API"
        assert payload["docs"] == "/docs"
        assert payload["api_prefix"] == "/api/v1"


def test_liveness_and_readiness_probes():
    with TestClient(create_app("sqlite+pysqlite:///:memory:")) as client:
        assert client.get("/health").json()["status"] == "ok"
        ready = client.get("/health/ready")
        assert ready.status_code == 200
        assert ready.json() == {"status": "ready", "database": "connected"}


def test_openapi_contains_expected_modules():
    with TestClient(create_app("sqlite+pysqlite:///:memory:")) as client:
        schema = client.get("/openapi.json").json()
        paths = schema["paths"]
        for path in ("/health", "/api/v1/auth/register", "/api/v1/projects/", "/api/v1/tasks/", "/api/v1/dashboard/summary"):
            assert path in paths


def test_dashboard_summary_handles_empty_tasks():
    """Validates that dashboard summary does not crash with ZeroDivisionError when no tasks exist."""
    with TestClient(create_app("sqlite+pysqlite:///:memory:")) as client:
        response = client.get("/api/v1/dashboard/summary")
        # Currently crashes with 500 Internal Server Error (ZeroDivisionError)
        assert response.status_code == 200
        payload = response.json()
        assert payload["total_tasks"] == 0
        assert payload["completed_tasks"] == 0
        assert payload["completion_rate"] == 0.0