from __future__ import annotations

import os
from enum import StrEnum, auto
from typing import Literal

import mcp
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class RetrieverOptions(BaseModel):
    collection_name: str = Field(description="Use just project id")
    filename_search: bool = Field(default=False, description="Enable filename search")
    composite_query_detection: bool = Field(
        default=False, description="Split composite query into several simple questions"
    )
    partial_search: bool = Field(
        default=False, description="Search by small chunks and take it`s neighbors."
    )
    query_rewrite: bool = Field(default=True, description="Enable rewriting user query")
    max_retrieved_docs: int = Field(
        default=4, description="Maximum number of documents to retrieve."
    )
    ranked_documents: int = Field(default=1, description="Number of ranked documents to return.")
    minimum_relevance: float = Field(
        default=0.5, description="Minimum relevance score for ranked documents."
    )


class EmbedderType(StrEnum):
    OPENAI = auto()
    VERTEX = auto()
    AZURE_OPENAI = auto()


class Embedder(BaseModel):
    embedder_type: str = Field(default=EmbedderType.VERTEX)


class SplitType(StrEnum):
    """Enum of text splitting methods."""

    CHARACTER = auto()
    SENTENCE = auto()
    PARAGRAPH = auto()
    SEMANTIC = auto()
    JSON = auto()


class ChunkingConfig(BaseModel):
    split_type: SplitType = Field(default=SplitType.JSON)
    chunk_size: int = Field(
        default=500,
    )
    chunk_overlap: int = Field(
        default=100,
    )


class RetrievalConfig(BaseModel):
    embedder: Embedder = Field(default_factory=Embedder)
    vector_database: Literal["qdrant", "chroma", "milvus"] = Field(default="qdrant")
    retriever_options: RetrieverOptions = Field(default_factory=RetrieverOptions)


class RagConfig(BaseModel):
    files_path: str = Field(description="Path to the folder with files")
    embedder: Embedder = Field(default_factory=Embedder)
    ranker: bool = Field(default=False)
    db_type: Literal["qdrant", "chroma", "milvus"] = Field(default="qdrant")
    retriever_options: RetrieverOptions = Field(default_factory=RetrieverOptions)
    chunking_options: ChunkingConfig = Field(default_factory=ChunkingConfig)


class RagConfigPlanArgs(BaseModel):
    project_id: str
    goal: str
    rag_config: RagConfig = Field(default_factory=RagConfig)


server = mcp.server.FastMCP(
    "rag-config-planner",
    log_level=os.getenv("RAGOPS_LOG_LEVEL", "WARNING"),  # noqa
)


@server.tool(
    name="rag_config_plan",
    description=(
        "Suggest a RAG configuration (vectorstore/chunking/retriever/ranker) "
        "for the given project and sources."
    ),
)
async def rag_config_plan(args: RagConfigPlanArgs) -> mcp.types.TextContent:
    plan = args.rag_config.model_dump_json()
    return mcp.types.TextContent(type="text", text=plan)


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
