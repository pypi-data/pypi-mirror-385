"""
MCP Server for managing docker-compose services for RagOps.

Provides tools to:
- List available services
- Initialize compose files in project
- Start/stop services
- Check service status
- Get logs
"""

import base64
import json
import os
import shutil
import subprocess
from enum import StrEnum, auto
from pathlib import Path
from typing import Literal

import mcp
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# Package root (where compose files are stored)
PACKAGE_ROOT = Path(__file__).parent.parent.parent
COMPOSE_DIR = PACKAGE_ROOT / "compose"
SERVICES_DIR = COMPOSE_DIR / "services"
TEMPLATES_DIR = COMPOSE_DIR / "templates"

# Compose file name
COMPOSE_FILE = "docker-compose.yml"

# Available services (using Docker Compose profiles)
AVAILABLE_SERVICES = {
    "qdrant": {
        "name": "qdrant",
        "description": "Qdrant vector database for RAG",
        "profile": "qdrant",
        "ports": ["6333:6333", "6334:6334"],
        "url": "http://localhost:6333",
    },
    "rag-service": {
        "name": "rag-service",
        "description": "RAG Query service",
        "profile": "rag-service",
        "ports": ["8000:8000"],
        "url": "http://localhost:8000",
    },
    "full-stack": {
        "name": "full-stack",
        "description": "Full RAG stack (Qdrant + RAG Service)",
        "profile": "full-stack",
        "ports": ["6333:6333", "8000:8000"],
        "url": "Multiple services",
    },
}


def check_docker_installed() -> tuple[bool, str]:
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, "Docker is running"
        return False, "Docker is installed but not running"
    except FileNotFoundError:
        return False, "Docker is not installed"
    except subprocess.TimeoutExpired:
        return False, "Docker command timed out"
    except Exception as e:
        return False, f"Error checking Docker: {str(e)}"


def check_docker_compose_installed() -> tuple[bool, str]:
    """Check if docker-compose is installed."""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "docker-compose command failed"
    except FileNotFoundError:
        # Try 'docker compose' (new syntax)
        try:
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
        except Exception:
            pass
        return False, "docker-compose is not installed"
    except Exception as e:
        return False, f"Error checking docker-compose: {str(e)}"


def get_compose_command() -> list[str]:
    """Get the appropriate docker-compose command."""
    # Try new syntax first
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            timeout=5,
            check=True,
        )
        return ["docker", "compose"]
    except Exception:
        pass

    # Fallback to old syntax
    return ["docker-compose"]


DEFAULT_PROMPT = """
You are an intelligent assistant designed to help users by 
providing accurate and concise answers based on the given context.

**Instructions:**
- Always respond in the same language as the user question
- Base your answers on the provided context
- If the context does not contain relevant information, clearly state that
- Be clear, concise, and helpful

**Context**: {context}

**Question**: {question}""".strip()


server = mcp.server.FastMCP(
    "ragops-compose-manager",
    log_level=os.getenv("RAGOPS_LOG_LEVEL", "WARNING"),  # noqa
)


# Create MCP server


class RetrieverType(StrEnum):
    MILVUS = auto()
    QDRANT = auto()
    CHROMA = auto()


class GenerationModelType(StrEnum):
    GEMINI = auto()
    OPENAI = auto()
    AZURE_OPENAI = auto()
    CLAUDE = auto()
    VERTEX = auto()


class EmbedderType(StrEnum):
    OPENAI = auto()
    VERTEX = auto()
    AZURE_OPENAI = auto()


class RagConfig(BaseModel):
    embedder_type: EmbedderType = Field(default=EmbedderType.VERTEX)
    vector_database: Literal["qdrant", "chroma", "milvus"] = Field(default="qdrant")
    generation_prompt: str = Field(default=DEFAULT_PROMPT)
    db_type: RetrieverType = RetrieverType.QDRANT
    database_uri: str = Field(
        default="http://qdrant:6333", description="Vector database URI inside DOCKER"
    )
    collection_name: str = Field(default="my_collection", description="Use project id")
    ranker: bool = Field(default=False)
    generation_model_type: GenerationModelType = GenerationModelType.VERTEX
    generation_model_name: str = "gemini-2.5-flash"
    max_retrieved_docs: int = Field(default=5)
    ranked_documents: int = Field(default=1)
    minimum_relevance: float = Field(default=0.75)
    query_rewrite: bool = Field(default=False)


def generate_env_file(
    rag_config: RagConfig | None,
    openai_api_key: str | None,
    azure_openai_api_key: str | None,
    azure_openai_endpoint: str | None,
    vertex_credentials_json: str | None,
    log_level: str | None,
) -> str:
    """Generate .env file content from RagConfig."""
    lines = [
        "# =============================================================================",
        "# RagOps Agent CE - Docker Compose Environment Variables",
        "# =============================================================================",
        "# Generated automatically by ragops-compose-manager",
        "",
        "# -----------------------------------------------------------------------------",
        "# LLM Provider Credentials",
        "# -----------------------------------------------------------------------------",
        "",
    ]

    # OpenAI
    lines.append("# OpenAI")
    lines.append(f"OPENAI_API_KEY={openai_api_key or ''}")
    lines.append("OPENAI_BASE_URL=")
    lines.append("")

    # Azure OpenAI - названия соответствуют Settings в rag_service/core/settings.py
    lines.append("# Azure OpenAI")
    lines.append(f"AZURE_OPENAI_API_KEY={azure_openai_api_key or ''}")
    lines.append(f"AZURE_OPENAI_AZURE_ENDPOINT={azure_openai_endpoint or ''}")
    lines.append("AZURE_OPENAI_API_VERSION=2024-02-15-preview")
    lines.append("AZURE_OPENAI_DEPLOYMENT_NAME=")
    lines.append("")

    # Vertex AI
    lines.append("# Vertex AI (Google Cloud)")
    lines.append("# Pass credentials as base64-encoded JSON")
    if vertex_credentials_json:
        # Encode to base64 to avoid issues with special characters in .env
        encoded = base64.b64encode(vertex_credentials_json.encode("utf-8")).decode("utf-8")
        lines.append(f"RAGOPS_VERTEX_CREDENTIALS_JSON={encoded}")
    else:
        lines.append("RAGOPS_VERTEX_CREDENTIALS_JSON=")
    lines.append("")

    lines.append("# -----------------------------------------------------------------------------")
    lines.append("# RAG Service Configuration")
    lines.append("# -----------------------------------------------------------------------------")
    lines.append("")

    # Database URI
    if rag_config:
        lines.append(f"DATABASE_URI={rag_config.database_uri}")
    else:
        lines.append("DATABASE_URI=http://qdrant:6333")
    lines.append("")

    # RAG Config JSON - переменная называется CONFIG в Settings
    # Encode to base64 to avoid issues with special characters in .env
    if rag_config:
        config_json = rag_config.model_dump_json()
        encoded_config = base64.b64encode(config_json.encode("utf-8")).decode("utf-8")
        lines.append("# RAG Configuration (auto-generated from RagConfig, base64-encoded)")
        lines.append(f"CONFIG={encoded_config}")
    else:
        lines.append("CONFIG=")

    lines.append("")
    lines.append("# -----------------------------------------------------------------------------")
    lines.append("# Server Settings")
    lines.append("# -----------------------------------------------------------------------------")
    lines.append("")

    level = log_level or "INFO"
    lines.append(f"LOG_LEVEL={level}")
    lines.append("")

    return "\n".join(lines)


class InitProjectComposeArgs(BaseModel):
    project_path: str = Field(
        description="Path to the project directory(auto create - use projects/<project_id>)"
    )
    rag_config: RagConfig | None = Field(None, description="RAG service configuration")


class ServicePort(BaseModel):
    """Custom port mapping for a service."""

    service: Literal["qdrant", "rag-service"] = Field(description="Service name")
    port: str = Field(
        description="Host port mapping in format 'host_port:container_port' (e.g., '6335:6333') "
        "or just host port (e.g., '6335')"
    )


class StartServiceArgs(BaseModel):
    service: Literal["qdrant", "rag-service", "full-stack"] = Field(
        description="Service name (qdrant, rag-service, full-stack)"
    )
    project_path: str | None = Field(".", description="Path to the project directory")
    detach: bool = Field(True, description="Run in detached mode")
    build: bool = Field(False, description="Build images before starting")
    custom_ports: list[ServicePort] | None = Field(
        None,
        description=(
            "Custom port mappings for services. "
            "Example: [{'service': 'qdrant', 'port': '6335:6333'}, "
            "{'service': 'rag-service', 'port': '8001:8000'}]"
        ),
    )


class StopServiceArgs(BaseModel):
    service: str = Field(description="Service name")
    project_path: str | None = Field(".", description="Path to the project directory")
    remove_volumes: bool = Field(False, description="Remove volumes")


class ServiceStatusArgs(BaseModel):
    service: str | None = Field(None, description="Service name (optional, default: all)")
    project_path: str | None = Field(".", description="Path to the project directory")


class GetLogsArgs(BaseModel):
    service: str = Field(description="Service name")
    tail: int = Field(100, description="Number of lines to show")
    project_path: str | None = Field(".", description="Path to the project directory")


@server.tool(
    name="list_available_services",
    description="Get list of available Docker Compose services that can be started",
)
async def list_available_services() -> mcp.types.TextContent:
    """List available services."""
    result = {
        "services": list(AVAILABLE_SERVICES.values()),
        "compose_dir": str(SERVICES_DIR),
    }
    return mcp.types.TextContent(type="text", text=json.dumps(result, indent=2))


@server.tool(
    name="init_project_compose",
    description="Initialize docker-compose file in the project directory with RAG configuration",
)
async def init_project_compose(args: InitProjectComposeArgs) -> mcp.types.TextContent:
    """Initialize compose files in project."""
    project_path = Path(args.project_path).resolve()

    # Create compose directory
    compose_target = project_path / "compose"
    compose_target.mkdir(parents=True, exist_ok=True)

    copied_files = []

    # Copy single docker-compose.yml file
    source = SERVICES_DIR / COMPOSE_FILE
    target = compose_target / COMPOSE_FILE

    if source.exists():
        shutil.copy2(source, target)
        copied_files.append(f"compose/{COMPOSE_FILE}")
    else:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {"status": "error", "message": f"Source compose file not found: {source}"}
            ),
        )

    # Read Vertex credentials if path provided
    vertex_credentials_json = None
    vertex_creds_path = os.getenv("RAGOPS_VERTEX_CREDENTIALS")
    if vertex_creds_path and Path(vertex_creds_path).exists():
        try:
            # Read and minify JSON (remove whitespace)
            creds_data = json.loads(Path(vertex_creds_path).read_text())
            vertex_credentials_json = json.dumps(creds_data, separators=(",", ":"))
        except Exception:
            pass  # If reading fails, will pass None

    # Generate .env file with RAG configuration
    env_content = generate_env_file(
        rag_config=args.rag_config,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        vertex_credentials_json=vertex_credentials_json,
        log_level=os.getenv("RAGOPS_LOG_LEVEL"),
    )
    env_file = compose_target / ".env"
    env_file.write_text(env_content)
    copied_files.append("compose/.env")
    result = {
        "status": "success",
        "copied_files": copied_files,
        "message": f"Compose files initialized in {compose_target}",
        "rag_config_applied": args.rag_config is not None,
    }

    return mcp.types.TextContent(type="text", text=json.dumps(result, indent=2))


@server.tool(
    name="start_service",
    description="Start a Docker Compose service",
)
async def start_service(args: StartServiceArgs) -> mcp.types.TextContent:
    """Start a service."""
    service = args.service
    project_path = Path(args.project_path).resolve()
    detach = args.detach
    build = args.build

    # Check Docker
    docker_ok, docker_msg = check_docker_installed()
    if not docker_ok:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": docker_msg}),
        )

    compose_ok, compose_msg = check_docker_compose_installed()
    if not compose_ok:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": compose_msg}),
        )

    # Check service exists
    if service not in AVAILABLE_SERVICES:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "error",
                    "message": f"Unknown service: {service}. "
                    f"Available: {list(AVAILABLE_SERVICES.keys())}",
                }
            ),
        )

    # Get compose file and profile
    compose_file = project_path / "compose" / COMPOSE_FILE
    profile = AVAILABLE_SERVICES[service]["profile"]

    if not compose_file.exists():
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "status": "error",
                    "message": f"Compose file not found: {compose_file}. "
                    f"Run init_project_compose first.",
                }
            ),
        )

    # Build command with profile
    cmd = get_compose_command()
    cmd.extend(["-f", str(compose_file), "--profile", profile, "up"])

    if detach:
        cmd.append("-d")
    if build:
        cmd.append("--build")

    # Set custom ports via environment variables if provided
    env = os.environ.copy()
    if args.custom_ports:
        # Create a mapping for easy lookup
        port_map = {sp.service: sp.port for sp in args.custom_ports}

        # For qdrant: QDRANT_PORT_HTTP and QDRANT_PORT_GRPC
        # For rag-service: RAG_SERVICE_PORT
        if service == "qdrant" and "qdrant" in port_map:
            port_mapping = port_map["qdrant"]
            if ":" in port_mapping:
                host_port = port_mapping.split(":")[0]
                env["QDRANT_PORT_HTTP"] = host_port
                # Assume GRPC port is HTTP port + 1
                env["QDRANT_PORT_GRPC"] = str(int(host_port) + 1)
        elif service == "rag-service" and "rag-service" in port_map:
            port_mapping = port_map["rag-service"]
            if ":" in port_mapping:
                host_port = port_mapping.split(":")[0]
                env["RAG_SERVICE_PORT"] = host_port
        elif service == "full-stack":
            # Apply both if available
            if "qdrant" in port_map:
                port_mapping = port_map["qdrant"]
                if ":" in port_mapping:
                    host_port = port_mapping.split(":")[0]
                    env["QDRANT_PORT_HTTP"] = host_port
                    env["QDRANT_PORT_GRPC"] = str(int(host_port) + 1)
            if "rag-service" in port_map:
                port_mapping = port_map["rag-service"]
                if ":" in port_mapping:
                    host_port = port_mapping.split(":")[0]
                    env["RAG_SERVICE_PORT"] = host_port

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_path,
            timeout=120,
            env=env,
        )

        if result.returncode == 0:
            service_info = AVAILABLE_SERVICES[service]
            # Use custom ports if provided, otherwise use default
            ports = service_info["ports"]
            url = service_info.get("url")

            if args.custom_ports:
                # Create a mapping for easy lookup
                port_map = {sp.service: sp.port for sp in args.custom_ports}

                if service == "qdrant" and "qdrant" in port_map:
                    port_mapping = port_map["qdrant"]
                    host_port = port_mapping.split(":")[0] if ":" in port_mapping else port_mapping
                    ports = [port_mapping, f"{int(host_port)+1}:6334"]
                    url = f"http://localhost:{host_port}"
                elif service == "rag-service" and "rag-service" in port_map:
                    port_mapping = port_map["rag-service"]
                    host_port = port_mapping.split(":")[0] if ":" in port_mapping else port_mapping
                    ports = [port_mapping]
                    url = f"http://localhost:{host_port}"

            return mcp.types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success",
                        "service": service,
                        "message": f"{service_info['description']} started successfully",
                        "url": url,
                        "ports": ports,
                        "custom_ports_applied": args.custom_ports is not None,
                        "output": result.stdout,
                    },
                    indent=2,
                ),
            )
        else:
            return mcp.types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": "Failed to start service",
                        "error": result.stderr,
                    }
                ),
            )

    except subprocess.TimeoutExpired:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": "Command timed out after 120 seconds"}),
        )
    except Exception as e:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": str(e)}),
        )


@server.tool(
    name="stop_service",
    description="Stop a Docker Compose service",
)
async def stop_service(args: StopServiceArgs) -> mcp.types.TextContent:
    """Stop a service."""
    service = args.service
    project_path = Path(args.project_path).resolve()
    remove_volumes = args.remove_volumes

    if service not in AVAILABLE_SERVICES:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": f"Unknown service: {service}"}),
        )

    compose_file = project_path / "compose" / COMPOSE_FILE
    profile = AVAILABLE_SERVICES[service]["profile"]

    if not compose_file.exists():
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {"status": "error", "message": f"Compose file not found: {compose_file}"}
            ),
        )

    cmd = get_compose_command()
    cmd.extend(["-f", str(compose_file), "--profile", profile, "down"])

    if remove_volumes:
        cmd.append("-v")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_path, timeout=60)

        if result.returncode == 0:
            return mcp.types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success",
                        "service": service,
                        "message": f"{service} stopped successfully",
                        "output": result.stdout,
                    },
                    indent=2,
                ),
            )
        else:
            return mcp.types.TextContent(
                type="text",
                text=json.dumps(
                    {"status": "error", "message": "Failed to stop service", "error": result.stderr}
                ),
            )

    except Exception as e:
        return mcp.types.TextContent(
            type="text", text=json.dumps({"status": "error", "message": str(e)})
        )


@server.tool(
    name="service_status",
    description="Check status of Docker Compose services",
)
async def service_status(args: ServiceStatusArgs) -> mcp.types.TextContent:
    """Check service status."""
    service = args.service
    project_path = Path(args.project_path).resolve()

    compose_dir = project_path / "compose"

    if not compose_dir.exists():
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": "Compose directory not found"}),
        )

    # Get list of services to check
    services_to_check = [service] if service else list(AVAILABLE_SERVICES.keys())

    compose_file = compose_dir / COMPOSE_FILE

    if not compose_file.exists():
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {"status": "error", "message": f"Compose file not found: {compose_file}"}
            ),
        )

    statuses = []
    cmd = get_compose_command()

    for svc in services_to_check:
        if svc not in AVAILABLE_SERVICES:
            continue

        profile = AVAILABLE_SERVICES[svc]["profile"]

        try:
            result = subprocess.run(
                [*cmd, "-f", str(compose_file), "--profile", profile, "ps", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout:
                containers = (
                    json.loads(result.stdout)
                    if result.stdout.startswith("[")
                    else [json.loads(result.stdout)]
                )
                statuses.append(
                    {
                        "service": svc,
                        "status": "running" if containers else "stopped",
                        "containers": containers,
                    }
                )
            else:
                statuses.append({"service": svc, "status": "stopped", "containers": []})

        except Exception as e:
            statuses.append({"service": svc, "status": "error", "error": str(e)})

    return mcp.types.TextContent(type="text", text=json.dumps({"services": statuses}, indent=2))


@server.tool(
    name="get_logs",
    description="Get logs from a Docker Compose service",
)
async def get_logs(args: GetLogsArgs) -> mcp.types.TextContent:
    """Get service logs."""
    service = args.service
    tail = args.tail
    project_path = Path(args.project_path).resolve()

    if service not in AVAILABLE_SERVICES:
        return mcp.types.TextContent(
            type="text",
            text=json.dumps({"status": "error", "message": f"Unknown service: {service}"}),
        )

    compose_file = project_path / "compose" / COMPOSE_FILE
    profile = AVAILABLE_SERVICES[service]["profile"]

    if not compose_file.exists():
        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {"status": "error", "message": f"Compose file not found: {compose_file}"}
            ),
        )

    cmd = get_compose_command()
    cmd.extend(["-f", str(compose_file), "--profile", profile, "logs", "--tail", str(tail)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_path, timeout=30)

        return mcp.types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "service": service,
                    "logs": result.stdout,
                },
                indent=2,
            ),
        )

    except Exception as e:
        return mcp.types.TextContent(
            type="text", text=json.dumps({"status": "error", "message": str(e)})
        )


def main() -> None:
    """Run the MCP server."""
    print("Compose manager server starting")
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
