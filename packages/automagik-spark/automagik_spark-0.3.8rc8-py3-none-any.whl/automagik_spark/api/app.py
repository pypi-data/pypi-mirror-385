"""Main FastAPI application module."""

import datetime
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import httpx

import tomllib
from pathlib import Path


def _get_version():
    """Get version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "unknown"


__version__ = _get_version()
from .config import get_cors_origins
from ..core.config import get_settings
from .dependencies import verify_api_key
from .routers import tasks, workflows, schedules, sources

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle FastAPI application startup and shutdown."""
    # Skip auto-discovery in test environment to avoid database contamination
    import os

    env = os.getenv("ENVIRONMENT")
    print(f"[LIFESPAN] Environment: {env}")
    if env != "testing":
        print("[LIFESPAN] Running auto-discovery...")
        # Startup - Auto-discover workflow sources
        await auto_discover_langflow()
        await auto_discover_automagik_agents()
    else:
        print("[LIFESPAN] Skipping auto-discovery for testing environment")

    # Log telemetry status
    _log_telemetry_status()

    yield
    # Shutdown (if needed)
    pass


def _log_telemetry_status():
    """Log telemetry status on startup."""
    from ..core.telemetry import is_telemetry_enabled

    if is_telemetry_enabled():
        logger.info("📊 Telemetry is ENABLED - helps us improve Automagik Spark")
        logger.info(
            "   • We collect anonymous usage analytics (commands, API usage, performance)"
        )
        logger.info(
            "   • No personal data, credentials, or workflow content is collected"
        )
        logger.info("   • Disable: export AUTOMAGIK_SPARK_DISABLE_TELEMETRY=true")
        logger.info("   • More info: automagik-spark telemetry info")
    else:
        logger.info("📊 Telemetry is DISABLED")


async def auto_discover_langflow():
    """Auto-discover LangFlow on ports 7860 and 7860 during startup."""
    langflow_ports = [7860, 7860]

    for port in langflow_ports:
        try:
            url = f"http://localhost:{port}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    logger.info(f"LangFlow detected on port {port}")

                    # Check if source already exists
                    from ..core.database.session import get_async_session
                    from ..core.database.models import WorkflowSource
                    from sqlalchemy import select

                    async with get_async_session() as session:
                        existing_source = await session.execute(
                            select(WorkflowSource).where(WorkflowSource.url == url)
                        )
                        if not existing_source.scalar_one_or_none():
                            # Get version info
                            version_info = None
                            try:
                                version_response = await client.get(
                                    f"{url}/api/v1/version"
                                )
                                if version_response.status_code == 200:
                                    version_info = version_response.json()
                            except:
                                pass

                            # Auto-add the LangFlow source
                            from ..core.schemas.source import SourceType

                            # Generate a descriptive name

                            new_source = WorkflowSource(
                                source_type=SourceType.LANGFLOW,
                                url=url,
                                encrypted_api_key=WorkflowSource.encrypt_api_key(
                                    "namastex888"
                                ),  # Standard API key across suite
                                version_info=version_info,
                                status="active",
                            )
                            session.add(new_source)
                            await session.commit()
                            logger.info(f"Auto-added LangFlow source at {url}")
                        else:
                            logger.info(f"LangFlow source already exists at {url}")

                    return  # Exit after finding the first LangFlow instance
                else:
                    logger.debug(f"LangFlow not available on port {port}")
        except Exception as e:
            logger.debug(f"LangFlow auto-discovery failed for port {port}: {e}")

    logger.info("No LangFlow instances found on ports 7860 or 7860")


async def auto_discover_automagik_agents():
    """Auto-discover AutoMagik Agents during startup."""
    from .config import get_agents_api_host, get_agents_api_port

    try:
        host = get_agents_api_host()
        port = get_agents_api_port()
        url = f"http://{host}:{port}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                logger.info(f"AutoMagik Agents detected on {host}:{port}")

                # Check if source already exists
                from ..core.database.session import get_async_session
                from ..core.database.models import WorkflowSource
                from sqlalchemy import select

                async with get_async_session() as session:
                    existing_source = await session.execute(
                        select(WorkflowSource).where(WorkflowSource.url == url)
                    )
                    if not existing_source.scalar_one_or_none():
                        # Get version info from root endpoint
                        version_info = None
                        try:
                            root_response = await client.get(url)
                            if root_response.status_code == 200:
                                root_data = root_response.json()
                                version_info = {
                                    "version": root_data.get("version", "unknown")
                                }
                        except:
                            pass

                        # Auto-add the AutoMagik Agents source
                        from ..core.schemas.source import SourceType

                        # Generate a descriptive name

                        new_source = WorkflowSource(
                            source_type=SourceType.AUTOMAGIK_AGENTS,
                            url=url,
                            encrypted_api_key=WorkflowSource.encrypt_api_key(
                                "namastex888"
                            ),  # Default API key for local instance
                            version_info=version_info,
                            status="active",
                        )
                        session.add(new_source)
                        await session.commit()
                        logger.info(f"Auto-added AutoMagik Agents source at {url}")

                        # Auto-sync the "simple" agent if it exists
                        await auto_sync_simple_agent(session, new_source)
                    else:
                        logger.info(f"AutoMagik Agents source already exists at {url}")

                        # Try to sync the "simple" agent if it doesn't exist yet
                        await auto_sync_simple_agent(
                            session, existing_source.scalar_one_or_none()
                        )
            else:
                logger.info(f"AutoMagik Agents not available on {host}:{port}")
    except Exception as e:
        logger.info(f"AutoMagik Agents auto-discovery failed: {e}")


async def auto_sync_simple_agent(session, source):
    """Auto-sync the 'simple' agent from AutoMagik Agents source."""
    if not source:
        return

    try:
        from ..core.database.models import Workflow
        from ..core.workflows.manager import WorkflowManager
        from sqlalchemy import select

        # Check if 'simple' agent is already synced
        existing_workflow = await session.execute(
            select(Workflow).where(
                Workflow.workflow_source_id == source.id,
                Workflow.remote_flow_id == "simple",
            )
        )

        if existing_workflow.scalar_one_or_none():
            logger.info("Simple agent already synced from AutoMagik Agents")
            return

        # Try to sync the 'simple' agent
        workflow_manager = WorkflowManager(session)
        try:
            workflow_data = await workflow_manager.sync_flow(
                flow_id="simple",
                input_component="",  # AutoMagik Agents don't use components
                output_component="",  # AutoMagik Agents don't use components
                source_url=source.url,
            )
            logger.info(
                f"Auto-synced 'simple' agent from AutoMagik Agents: {workflow_data.get('id')}"
            )
        except Exception as sync_error:
            # This is expected if no API key is configured or agent doesn't exist
            logger.debug(f"Could not auto-sync 'simple' agent: {sync_error}")

    except Exception as e:
        logger.debug(f"Auto-sync simple agent failed: {e}")


app = FastAPI(
    title="Spark API",
    description="Spark - Automated workflow management with LangFlow integration",
    version=__version__,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema to include security components
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add API Key security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key authentication",
        }
    }

    # Apply security to all endpoints except those that don't need auth
    security_requirement = [{"APIKeyHeader": []}]

    # These endpoints don't require authentication
    no_auth_paths = [
        "/health",
        "/",
        "/api/v1/docs",
        "/api/v1/redoc",
        "/api/v1/openapi.json",
    ]

    # Update security for each path
    for path, path_item in openapi_schema["paths"].items():
        if path not in no_auth_paths:
            for operation in path_item.values():
                operation["security"] = security_requirement

                # Add authentication description to each endpoint
                if "description" in operation:
                    operation[
                        "description"
                    ] += "\n\n**Requires Authentication**: This endpoint requires an API key."
                else:
                    operation["description"] = (
                        "**Requires Authentication**: This endpoint requires an API key."
                    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set the custom OpenAPI schema
# Type ignore: FastAPI allows dynamic method assignment for custom OpenAPI schema
# This is the documented way to customize OpenAPI schema generation
app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/health")
async def health():
    """Health check endpoint with API and worker status"""
    from ..core.celery.celery_app import app as celery_app
    import redis
    import os

    current_time = datetime.datetime.now()

    # Check API status (if we're responding, API is healthy)
    api_status = "healthy"

    # Check worker status by inspecting Celery workers
    worker_status = "unknown"
    worker_details = {"active_workers": 0, "available_tasks": []}

    try:
        # Get active workers from Celery
        inspect = celery_app.control.inspect()
        active_workers = inspect.active_queues()

        if active_workers:
            worker_status = "healthy"
            worker_details["active_workers"] = len(active_workers)
            # Get available tasks
            registered_tasks = inspect.registered()
            if registered_tasks:
                # Flatten task lists from all workers
                all_tasks = []
                for worker_tasks in registered_tasks.values():
                    all_tasks.extend(worker_tasks)
                worker_details["available_tasks"] = list(set(all_tasks))
        else:
            worker_status = "unhealthy"
    except Exception as e:
        worker_status = "error"
        worker_details["error"] = str(e)

    # Check Redis connectivity (Celery broker)
    redis_status = "unknown"
    try:
        broker_url = os.getenv(
            "AUTOMAGIK_SPARK_CELERY_BROKER_URL", "redis://localhost:6379/0"
        )
        # Parse Redis URL
        if broker_url.startswith("redis://"):
            redis_client = redis.from_url(broker_url)
            redis_client.ping()
            redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    # Determine overall status
    overall_status = "healthy"
    if worker_status in ["unhealthy", "error"] or redis_status == "unhealthy":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": {
            "api": {"status": api_status, "version": __version__},
            "worker": {"status": worker_status, **worker_details},
            "redis": {"status": redis_status},
        },
    }


@app.get("/")
async def root(api_key: str = Depends(verify_api_key)):
    """Root endpoint returning API status"""
    current_time = datetime.datetime.now()
    settings = get_settings()
    base_url = settings.remote_url
    return {
        "status": "online",
        "service": "Spark API",
        "message": "Welcome to Spark API, it's up and running!",
        "version": __version__,
        "server_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "docs_url": f"{base_url}/api/v1/docs",
        "redoc_url": f"{base_url}/api/v1/redoc",
        "openapi_url": f"{base_url}/api/v1/openapi.json",
    }


# Add routers with /api/v1 prefix
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
