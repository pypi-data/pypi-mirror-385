"""FastAPI application factory with simplified ServiceConfig (v2)."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from beanie import Document
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from ..auth.exception_handlers import register_auth_exception_handlers
from ..auth.init_data import create_first_super_admin
from ..auth.models import OAuthAccount, User
from ..health import create_health_router
from .config import settings
from .db import init_mongo
from .logging_config import get_logger, setup_logging
from .service_types import ServiceConfig

setup_logging()
logger = get_logger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique ID for each route based on its tags and name."""
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


def create_lifespan(
    service_config: ServiceConfig, document_models: list[type[Document]] | None = None
) -> Callable:
    """Create lifespan context manager for the application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        # Startup
        startup_tasks = []

        # Initialize database if enabled
        if service_config.enable_database and document_models:
            # Prepare models list (make a copy to avoid modifying the original)
            models_to_init = list(document_models)

            if service_config.enable_auth:
                # Ensure auth models are included
                auth_models = [User, OAuthAccount]
                for model in auth_models:
                    if model not in models_to_init:
                        models_to_init.append(model)
            try:
                client = await init_mongo(
                    models_to_init,
                    service_config.service_name,
                )
                startup_tasks.append(("mongodb_client", client))
                logger.info(
                    f"✅ Connected to MongoDB for {service_config.service_name}"
                )

                # Create first super admin after database initialization
                if service_config.enable_auth:
                    await create_first_super_admin()

            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {e}")
                if not settings.MOCK_DATABASE:
                    raise
                logger.warning("🔄 Running with mock database")

        # Store startup tasks in app state
        app.state.startup_tasks = startup_tasks

        # Run custom lifespan if provided
        if service_config.lifespan:
            async with service_config.lifespan(app):
                yield
        else:
            yield

        # Shutdown
        for task_name, task_obj in startup_tasks:
            if task_name == "mongodb_client":
                try:
                    task_obj.close()
                    logger.info("✅ Disconnected from MongoDB")
                except Exception as e:
                    logger.error(f"⚠️ Error disconnecting from MongoDB: {e}")

    return lifespan


def create_fastapi_app(
    service_config: ServiceConfig,
    document_models: list[type[Document]] | None = None,
) -> FastAPI:
    """Create a standardized FastAPI application with simplified ServiceConfig.

    Args:
        service_config: 통합 서비스 설정 (ServiceConfig)
        document_models: List of Beanie document models

    Returns:
        Configured FastAPI application
    """
    # Application metadata
    app_title = (
        f"{settings.PROJECT_NAME} - "
        f"{(service_config.service_name).replace('_', ' ').title()} "
        f"[{(settings.ENVIRONMENT).capitalize()}]"
    )
    app_description = (
        service_config.description
        or f"{service_config.service_name} for Quant Platform"
    )

    # Check if we're in development
    is_development = settings.ENVIRONMENT in ["development", "local"]

    # Create lifespan
    lifespan_func = create_lifespan(service_config, document_models)

    # Create FastAPI app
    app = FastAPI(
        title=app_title,
        description=app_description,
        version=service_config.service_version,
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=lifespan_func,
        docs_url="/docs" if is_development else None,
        redoc_url="/redoc" if is_development else None,
        openapi_url="/openapi.json" if is_development else None,
    )

    # Add CORS middleware
    final_cors_origins = service_config.cors_origins or settings.all_cors_origins
    if final_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=final_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add authentication middleware (개선된 조건부 적용)
    if service_config.enable_auth:
        try:
            from ..auth.middleware import AuthMiddleware

            app.add_middleware(AuthMiddleware, service_config=service_config)
            
            auth_status = "enabled"
            if is_development:
                auth_status += " (development mode - fallback authentication available)"
            
            logger.info(f"🔐 Authentication middleware {auth_status} for {service_config.service_name}")
            
        except ImportError as e:
            logger.warning(f"⚠️ Authentication middleware not available: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to add authentication middleware: {e}")
            if not is_development:
                raise  # 프로덕션에서는 인증 실패 시 앱 시작 중단
    else:
        logger.info(f"🔓 Authentication disabled for {service_config.service_name}")

    # Add metrics middleware with graceful fallback
    if service_config.enable_metrics:
        try:
            from ..metrics import (
                MetricsMiddleware,
                create_metrics_middleware,
                get_metrics_collector,
            )

            # Initialize metrics collector first
            create_metrics_middleware(service_config.service_name)
            # Add middleware with collector
            collector = get_metrics_collector()
            app.add_middleware(MetricsMiddleware, collector=collector)
            logger.info(
                f"📊 Metrics middleware enabled for {service_config.service_name}"
            )
        except ImportError:
            logger.warning(
                f"⚠️ Metrics middleware not available for {service_config.service_name}"
            )
        except Exception as e:
            logger.warning(
                f"⚠️ Failed to add metrics middleware for {service_config.service_name}: {e}"
            )

    # Add health check endpoints
    if service_config.enable_health_check:
        health_router = create_health_router(
            service_config.service_name, service_config.service_version
        )
        app.include_router(health_router)
        logger.info(f"❤️ Health check endpoints added for {service_config.service_name}")

    # Include auth routers if enabled
    if service_config.enable_auth:
        from ..auth.router import auth_router, user_router

        app.include_router(
            auth_router, prefix=f"/api/{settings.AUTH_API_VERSION}/auth", tags=["Auth"]
        )
        app.include_router(
            user_router, prefix=f"/api/{settings.AUTH_API_VERSION}/users", tags=["User"]
        )
        # Register auth exception handlers
        register_auth_exception_handlers(app)
        logger.info(
            f"🔐 Auth routes and exception handlers added for {service_config.service_name}"
        )
        # Include OAuth2 routers if enabled
        if service_config.enable_oauth:
            try:
                from ..auth.router import oauth2_router

                app.include_router(
                    oauth2_router,
                    prefix=f"/api/{settings.AUTH_API_VERSION}",
                )
                logger.info(f"🔐 OAuth2 routes added for {service_config.service_name}")
            except Exception as e:
                logger.error(f"⚠️ Failed to include OAuth2 router: {e}")

    return app
