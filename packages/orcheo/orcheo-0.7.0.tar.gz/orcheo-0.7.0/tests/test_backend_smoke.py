"""Smoke tests for the FastAPI deployment wrapper."""

from importlib import import_module
import pytest
from fastapi import FastAPI
from starlette.routing import WebSocketRoute


def test_backend_app_imports() -> None:
    """Ensure the deployment wrapper module imports without errors."""
    try:
        module = import_module("orcheo_backend.app")
    except ModuleNotFoundError as exc:  # pragma: no cover - aids debugging
        pytest.fail(f"Failed to import orcheo_backend.app: {exc}")
    assert hasattr(module, "app")
    assert hasattr(module, "create_app")


def test_create_app_returns_fastapi_instance() -> None:
    """Ensure the app factory returns FastAPI with the workflow websocket route."""
    module = import_module("orcheo_backend.app")
    app = module.create_app()
    assert isinstance(app, FastAPI)
    websocket_routes = [
        route for route in app.router.routes if isinstance(route, WebSocketRoute)
    ]
    websocket_paths = {route.path for route in websocket_routes}
    assert "/ws/workflow/{workflow_id}" in websocket_paths


def test_get_app_matches_module_level_app() -> None:
    """Verify the exported get_app helper returns the module-level FastAPI instance."""
    backend_module = import_module("orcheo_backend")
    module = import_module("orcheo_backend.app")
    get_app = backend_module.get_app

    assert isinstance(module.app, FastAPI)
    assert get_app() is module.app
