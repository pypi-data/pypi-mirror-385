"""
api/main.py
-----------
Aplicação FastAPI principal - Ontology Stack API.

Esta é uma implementação OSS da API de Ontologia do Palantir Foundry.

Arquitetura:
- Camada de Apresentação: FastAPI routers (REST endpoints)
- Camada de Serviço: Lógica de negócio
- Camada de Repositório: Acesso a dados
- Camada de Dados: SQLModel (relacional) + KuzuDB (grafo)

Para executar:
    uvicorn api.main:app --reload

Acesse a documentação em:
    http://localhost:8000/docs
"""

import asyncio
import contextlib
import os
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlmodel import Session, SQLModel, select

from api import mcp_router
from api.core.database import engine
from api.core.docs import (
    API_TAGS,
    DEFAULT_ERROR_COMPONENTS,
    SECURITY_SCHEMES,
    SERVERS_METADATA,
    SWAGGER_UI_PARAMETERS,
    api_error_schema,
)
from api.core.settings import get_settings
from api.core.temporal import connect_temporal
from api.dependencies import ensure_runtime_started, run_realtime_enricher, shutdown_runtime
from api.repositories.kuzudb_repository import get_kuzu_repo
from api.v2.routers import (
    action_types,
    actions,
    analytics,
    auth,
    change_sets,
    datasets,
    interfaces,
    link_types,
    linked_objects,
    migrations,
    object_types,
    objects,
    query_types,
    realtime,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("INFO: Iniciando Ontology Stack API...")
    print("INFO: Criando tabelas do metamodelo no banco de dados...")
    SQLModel.metadata.create_all(engine)
    print("INFO: Tabelas criadas com sucesso.")

    # Inicializar KuzuDB (o singleton já cria o schema)
    kuzu_repo = get_kuzu_repo()
    if kuzu_repo.is_available():
        print("INFO: KuzuDB inicializado e pronto.")
    else:
        print("WARNING: KuzuDB não disponível. Funcionalidades de grafo desabilitadas.")

    # Auto-load action modules to ensure executors are registered
    try:
        import api.actions.test_actions  # noqa: F401

        print("INFO: Actions executors loaded.")
    except Exception as e:
        print(f"WARNING: Failed to load actions executors: {e}")

    realtime_stop_event = asyncio.Event()
    try:
        await ensure_runtime_started()
        app.state.realtime_stop_event = realtime_stop_event
        app.state.realtime_task = asyncio.create_task(run_realtime_enricher(realtime_stop_event))
    except Exception as exc:  # pragma: no cover - enrichment startup is best-effort
        print(f"WARNING: Failed to start real-time enricher: {exc}")

    # Initialize Temporal client (singleton) if enabled
    app.state.temporal_client = None
    try:
        settings = get_settings()
        use_temporal = settings.use_temporal_actions or os.getenv("USE_TEMPORAL_ACTIONS", "0") in (
            "1",
            "true",
            "True",
        )
        if use_temporal:
            print("INFO: Initializing Temporal client…")
            app.state.temporal_client = await connect_temporal(settings)
            print("INFO: Temporal client ready.")
    except Exception as e:
        # Do not fail API startup if Temporal is misconfigured
        print(f"WARNING: Failed to initialize Temporal client: {e}")

    yield

    # Shutdown
    print("INFO: Encerrando Ontology Stack API...")
    if kuzu_repo.is_available():
        kuzu_repo.close()
    realtime_task = getattr(app.state, "realtime_task", None)
    realtime_stop = getattr(app.state, "realtime_stop_event", None)
    if realtime_stop is not None:
        realtime_stop.set()
    if realtime_task is not None:
        with contextlib.suppress(asyncio.CancelledError):
            await realtime_task
    await shutdown_runtime()
    # Drop Temporal client reference
    try:
        app.state.temporal_client = None
    except Exception:
        pass


# Criar aplicação FastAPI
_API_DESCRIPTION = """
The Ontologia Stack API delivers a production-ready surface for managing ontology metamodels,
instance data, link traversals, and long-running actions. It mirrors the ergonomics of Palantir
Foundry while embracing cloud-native primitives and modern Python tooling.

### Why Ontologia?
- **Programmatic Metamodeling** – Treat ObjectTypes, LinkTypes, Interfaces, and Actions as code.
- **Hybrid Query Engine** – Blend relational filtering with graph traversals in a single request.
- **Action Orchestration** – Execute business workflows synchronously or via Temporal.
- **Tenant-Aware Security** – JWT-based AuthN + RBAC with granular tenant scoping baked in.

Explore the endpoints below, supply a bearer token via the **Authorize** button, and use the
examples embedded in each response schema to jumpstart automation.
"""

app = FastAPI(
    title="Ontology Stack API",
    version="0.1.0",
    description=_API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=API_TAGS,
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
    contact={
        "name": "Ontologia Engineering",
        "url": "https://ontologia.example",
        "email": "engineering@ontologia.example",
    },
    license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
    terms_of_service="https://ontologia.example/terms",
)


# Configurar CORS para permitir acesso de frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routers ---


# Health check endpoint
@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.

    Returns:
        Status da API
    """
    return {
        "service": "Ontology Stack API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check detalhado.

    Returns:
        Status dos componentes
    """
    kuzu_repo = get_kuzu_repo()

    # DB connectivity probe
    db_status = "connected"
    try:
        with Session(engine) as s:
            s.exec(select(1))
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "components": {
            "api": "running",
            "database": db_status,
            "kuzudb": "available" if kuzu_repo.is_available() else "unavailable",
        },
    }


# Router "pai" para a ontologia (compatível com Foundry)
# Path: /v2/ontologies/{ontologyApiName}/...
v2_router = APIRouter(prefix="/v2/ontologies/{ontologyApiName}")
v2_router.include_router(object_types.router)
v2_router.include_router(link_types.router)
v2_router.include_router(
    actions.router
)  # Register before objects/traversal to prioritize static path
v2_router.include_router(action_types.router)
v2_router.include_router(objects.router)
v2_router.include_router(linked_objects.router)
v2_router.include_router(analytics.router)
v2_router.include_router(interfaces.router)
v2_router.include_router(query_types.router)
v2_router.include_router(datasets.router)
v2_router.include_router(change_sets.router)
v2_router.include_router(realtime.router)
v2_router.include_router(migrations.router)

app.include_router(v2_router)
app.include_router(auth.router, prefix="/v2/auth")
app.mount("/mcp", mcp_router.app)


def _build_openapi_schema():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=API_TAGS,
    )
    components = schema.setdefault("components", {})
    components.setdefault("schemas", {})["ApiError"] = api_error_schema()
    responses = components.setdefault("responses", {})
    responses.update(DEFAULT_ERROR_COMPONENTS["responses"])
    components.setdefault("securitySchemes", {}).update(SECURITY_SCHEMES)
    schema["servers"] = SERVERS_METADATA

    exempt_paths = {"/", "/health", "/v2/auth/token"}
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method == "parameters":
                continue
            operation.setdefault("responses", {}).setdefault(
                "500", {"$ref": "#/components/responses/ServerError"}
            )
            if path in exempt_paths:
                continue
            security = operation.setdefault("security", [])
            bearer_ref = {"BearerAuth": []}
            if bearer_ref not in security:
                security.append(bearer_ref)
            responses_map = operation.setdefault("responses", {})
            responses_map.setdefault("401", {"$ref": "#/components/responses/UnauthorizedError"})
            responses_map.setdefault("403", {"$ref": "#/components/responses/ForbiddenError"})
            responses_map.setdefault("429", {"$ref": "#/components/responses/TooManyRequestsError"})

    return schema


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = _build_openapi_schema()
    return app.openapi_schema


cast(Any, app).openapi = custom_openapi


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("ONTOLOGY STACK API")
    print("=" * 60)
    print("Iniciando servidor de desenvolvimento...")
    print("Documentação: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
