from __future__ import annotations

import json
import os
from pathlib import Path

import mcp
from donkit.chunker import ChunkerConfig, DonkitChunker
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field

load_dotenv()


class ChunkDocumentsArgs(BaseModel):
    source_path: str = Field(description="Path to the source directory")
    params: ChunkerConfig


server = mcp.server.FastMCP(
    "rag-chunker",
    log_level=os.getenv("RAGOPS_LOG_LEVEL", "WARNING"),  # noqa
)


@server.tool(
    name="chunk_documents",
    description=(
        "Reads documents from given paths, "
        "splits them into smaller text chunks, "
        "and returns the path to a JSON file with the result. "
        "Support only text file eg. .txt, .json"
    ).strip(),
)
async def chunk_documents(args: ChunkDocumentsArgs) -> mcp.types.TextContent:
    # Create a directory for output if it doesn't exist
    chunker = DonkitChunker(args.params)
    processed_files: list[Path] = []
    output_path = Path(args.source_path) / "chunked"
    output_path.mkdir(parents=True, exist_ok=True)

    source_dir = Path(args.source_path)
    if not source_dir.exists() or not source_dir.is_dir():
        return mcp.types.TextContent(type="text", text="Error: path not found")

    for file in source_dir.iterdir():
        # Skip directories, process only files
        if not file.is_file():
            continue

        try:
            chunked_documents = chunker.chunk_file(
                file_path=str(file),
            )
        except Exception as e:
            logger.error(f"Failed to chunk file {file}: {e}")
            continue

        output_file = output_path / f"{file.name}.json"
        try:
            payload = [
                {"page_content": chunk.page_content, "metadata": chunk.metadata}
                for chunk in chunked_documents
            ]
            output_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            processed_files.append(output_file)
        except Exception as e:
            logger.error(f"Failed to write chunks for {file} to {output_file}: {e}")
            continue

    # If no files were processed, return empty path
    if not processed_files:
        return mcp.types.TextContent(type="text", text="")

    # Return the path to the output directory containing chunked files
    return mcp.types.TextContent(type="text", text=str(output_path))


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
