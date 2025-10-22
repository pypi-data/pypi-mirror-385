import json
import os
from pathlib import Path
from typing import List, Optional

import mcp
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validate_call

load_dotenv()


class ChecklistItem(BaseModel):
    id: str
    description: str
    status: str = Field(default="pending")  # pending, in_progress, completed


class Checklist(BaseModel):
    name: str
    items: List[ChecklistItem]


server = mcp.server.FastMCP(
    "rag-checklist",
    log_level=os.getenv("RAGOPS_LOG_LEVEL", "WARNING"),  # noqa
)


def _save_checklist(checklist: Checklist) -> str:
    output_dir = Path("./ragops_checklists")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"checklist_{checklist.name}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(checklist.model_dump(), f, indent=2)
    return str(output_path)


def _load_checklist(name: str) -> Optional[Checklist]:
    output_path = Path("./ragops_checklists") / f"checklist_{name}.json"
    if not output_path.exists():
        return None
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
        return Checklist(**data)


@server.tool(
    name="create_checklist",
    description="Creates a new checklist with a given name and list of tasks.",
)
@validate_call
async def create_checklist(
    name: str,
    items: List[str],
) -> mcp.types.TextContent:
    # Convert simple string items to ChecklistItem objects
    checklist_items = [
        ChecklistItem(id=f"item_{i}", description=item) for i, item in enumerate(items)
    ]
    checklist = Checklist(name=name, items=checklist_items)
    output_path = _save_checklist(checklist)
    return mcp.types.TextContent(
        type="text",
        text=f"Checklist '{name}' created with {len(items)} items. Saved to {output_path}",
    )


@server.tool(
    name="get_checklist",
    description="Retrieves the current state of a checklist by its name as a JSON string.",
)
@validate_call
async def get_checklist(
    name: str,
) -> mcp.types.TextContent:
    checklist = _load_checklist(name)
    if checklist is None:
        return mcp.types.TextContent(type="text", text=f"Checklist '{name}' not found.")

    # Return the full checklist as a JSON string to provide all details, including IDs
    return mcp.types.TextContent(type="text", text=checklist.model_dump_json(indent=2))


@server.tool(
    name="update_checklist_item",
    description="Updates the status of a specific item in a checklist.",
)
@validate_call
async def update_checklist_item(
    name: str,
    item_id: str,
    status: str,
) -> mcp.types.TextContent:
    checklist = _load_checklist(name)
    if checklist is None:
        return mcp.types.TextContent(type="text", text=f"Checklist '{name}' not found.")

    found = False
    for item in checklist.items:
        if item.id == item_id:
            item.status = status
            found = True
            break

    if not found:
        return mcp.types.TextContent(
            type="text", text=f"Item '{item_id}' not found in checklist '{name}'."
        )

    _save_checklist(checklist)
    return mcp.types.TextContent(
        type="text",
        text=f"Updated item '{item_id}' in checklist '{name}' to status '{status}'.",
    )


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
