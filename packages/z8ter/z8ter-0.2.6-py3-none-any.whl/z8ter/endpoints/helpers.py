"""Endpoint utilities for rendering templates and loading page content.

This module provides helpers to:
  - Render a Jinja template into a Starlette `Response`.
  - Load structured YAML content for a page, keyed by `page_id`.

Conventions:
  - Content files live under BASE_DIR/content/{page_id}.yaml.
  - Templates are resolved via the app's Jinja2 environment.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml
from starlette.templating import Jinja2Templates

from z8ter import BASE_DIR, get_templates
from z8ter.responses import Response

contents_path = BASE_DIR / "content"

logger = logging.getLogger("z8ter")


def render(template_name: str, context: dict[str, Any] | None = None) -> Response:
    """Render a Jinja template into a Starlette `TemplateResponse`.

    Args:
        template_name: Path to the Jinja template, relative to templates dir.
        context: Template context variables. May be None.

    Returns:
        Response: A Starlette TemplateResponse object.

    Notes:
        - Unlike Starlette, this wrapper does not automatically inject `request`
          into the context. You may want to add it in higher-level view helpers.
        - Response type is framework-specific but generally behaves like ASGI.

    """
    templates: Jinja2Templates = get_templates()
    return templates.TemplateResponse(template_name, context)


def load_props(page_id: str, base: Path | None = None) -> dict[str, Any]:
    """Load page props for a given page id from content files.

    - Supports .json, .yaml, .yml (last match wins).
    - `page_id` may use dots or slashes: "app.home" -> "app/home".

    Args:
        page_id: Identifier like "about" or "app.home".
        base: Optional override for the content root (defaults to `contents_path`).

    Returns:
        {"page_content": <mapping>}

    Raises:
        json.JSONDecodeError / yaml.YAMLError: If content is malformed.

    """
    root = base if base is not None else contents_path
    rel = page_id.replace(".", "/")

    candidates = [
        root / f"{rel}.json",
        root / f"{rel}.yaml",
        root / f"{rel}.yml",
    ]

    for path in candidates:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".json":
                data = json.loads(text)
            else:
                data = yaml.safe_load(text)

    if data is None:
        data = {}
        logger.warning(f"No content found for '{page_id}' under {root})")
    return {"page_content": dict(data)}
