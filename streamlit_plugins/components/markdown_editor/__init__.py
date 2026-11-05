from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from streamlit.components.v2 import component as create_component
from streamlit.elements.lib.layout_utils import Height

_ASSET_DIR = Path(__file__).with_name("frontend") / "build"


def _normalize_blocks(
    blocks: Sequence[Mapping[str, Any]], *, for_review: bool = False
) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for index, block in enumerate(blocks):
        if not isinstance(block, Mapping):
            raise TypeError(f"El bloque {index} debe ser un mapping")
        markdown = block.get("markdown", block.get("text"))
        if not isinstance(markdown, str):
            raise TypeError(f"El bloque {index} debe incluir markdown de tipo str")
        block_id = block.get("id") if for_review else block.get("id", f"block-{index}")
        block_id = str(block_id) if block_id is not None or not for_review else None
        if block_id is not None and block_id in seen_ids:
            raise ValueError(f"ID de bloque duplicado: {block_id}")
        item = {"markdown": markdown}
        if block_id is not None:
            seen_ids.add(block_id)
            item["id"] = block_id
        normalized.append(item)
    if not normalized and not for_review:
        normalized.append({"id": "block-0", "markdown": ""})
    return normalized


def _normalize_diff(diff: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if diff is None:
        return None
    if not isinstance(diff, Mapping):
        raise TypeError("diff debe ser un mapping con before y after o sus bloques")
    has_blocks = "before_blocks" in diff or "after_blocks" in diff
    if has_blocks and not ("before_blocks" in diff and "after_blocks" in diff):
        raise ValueError("diff debe incluir before_blocks y after_blocks juntos")
    normalized: dict[str, Any] = {}
    for version in ("before", "after"):
        source = diff.get(version)
        if has_blocks:
            blocks = diff[f"{version}_blocks"]
            if not isinstance(blocks, Sequence) or isinstance(blocks, (str, bytes)):
                raise TypeError(f"{version}_blocks debe ser una secuencia de bloques")
            blocks = _normalize_blocks(blocks, for_review=True)
            normalized[f"{version}_blocks"] = blocks
            markdown = "\n\n".join(block["markdown"] for block in blocks)
            if source is None:
                source = markdown
            elif source != markdown:
                raise ValueError(f"{version} debe coincidir con el Markdown de {version}_blocks")
        if not isinstance(source, str):
            raise ValueError("diff debe incluir before y after de tipo str o sus bloques")
        normalized[version] = source
    return normalized


def _document_from_state(
    state: Any,
    initial_blocks: list[dict[str, str]],
    *,
    mode: str,
    save_mode: str,
) -> dict[str, Any]:
    if state is None:
        blocks = initial_blocks
        return {
            "blocks": blocks,
            "markdown": "\n\n".join(block["markdown"] for block in blocks),
            "mode": mode,
            "save_mode": save_mode,
        }
    if not isinstance(state, Mapping):
        raise TypeError("El estado devuelto por el editor debe ser un mapping")
    state_blocks = state.get("blocks")
    state_markdown = state.get("markdown")
    if not isinstance(state_blocks, list) or not isinstance(state_markdown, str):
        raise ValueError("El editor devolvió un estado incompleto")
    state_mode = state.get("mode", mode)
    if state_mode not in {"raw_visual", "visual"}:
        raise ValueError("El editor devolvió un modo desconocido")
    return {
        "blocks": state_blocks,
        "markdown": state_markdown,
        "mode": state_mode,
        "save_mode": save_mode,
    }


def st_markdown_block_editor(
    initial_blocks: Sequence[Mapping[str, Any]],
    *,
    key: str,
    revision: int = 0,
    height: Height | None = "stretch",
    mode: str = "raw_visual",
    save_mode: str = "auto",
    only_view: bool = False,
    debug_blocks: bool = False,
    diff: Mapping[str, Any] | None = None,
    editor_modes: Sequence[str] = ("raw_visual", "visual"),
    review_modes: Sequence[str] = ("visual", "markdown"),
    review_layouts: Sequence[str] = ("before", "after", "split", "blocks"),
    block_diff_style: str = "content",
    placeholder: str = "Escribe aquí…",
    show_copy_button: bool = True,
    show_status_bar: bool = True,
    toolbar_sections: Sequence[str] = ("view", "format", "block", "history", "changes"),
) -> dict[str, Any]:
    """Edit Markdown blocks or review visual, source and block-level changes.

    With button saving, review compares the saved document with the local draft.
    External diffs accept before/after strings or paired before_blocks/after_blocks.
    Stable block IDs improve movement and content-change identification.
    toolbar_sections controls header visibility, not editing permissions.
    """
    if not key:
        raise ValueError("key no puede estar vacía")
    if revision < 0:
        raise ValueError("revision no puede ser negativa")
    if height is not None and (isinstance(height, bool) or not isinstance(height, (int, str))):
        raise TypeError("height debe ser un entero, 'stretch', 'content' o None")
    if isinstance(height, int) and height < 240:
        raise ValueError("height debe ser al menos 240 px")
    if isinstance(height, str) and height not in {"stretch", "content"}:
        raise ValueError("height debe ser 'stretch' o 'content'")
    if mode not in {"raw_visual", "visual"}:
        raise ValueError("mode debe ser 'raw_visual' o 'visual'")
    if save_mode not in {"auto", "button"}:
        raise ValueError("save_mode debe ser 'auto' o 'button'")
    if not isinstance(only_view, bool):
        raise TypeError("only_view debe ser bool")
    if not isinstance(debug_blocks, bool):
        raise TypeError("debug_blocks debe ser bool")
    choices = {
        "editor_modes": (editor_modes, {"raw_visual", "visual"}, True),
        "review_modes": (review_modes, {"visual", "markdown"}, True),
        "review_layouts": (review_layouts, {"before", "after", "split", "blocks"}, True),
        "toolbar_sections": (toolbar_sections, {"view", "format", "block", "history", "changes"}, False),
    }
    for name, (values, allowed, required) in choices.items():
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            raise TypeError(f"{name} debe ser una secuencia de opciones")
        if (required and not values) or any(not isinstance(value, str) or value not in allowed for value in values):
            raise ValueError(f"{name}: opciones válidas {sorted(allowed)}" + ("; elige al menos una" if required else ""))
        if len(set(values)) != len(values):
            raise ValueError(f"{name} no puede incluir opciones duplicadas")
    if mode not in editor_modes:
        raise ValueError("mode debe estar incluido en editor_modes")
    if block_diff_style not in {"content", "inline"}:
        raise ValueError("block_diff_style debe ser 'content' o 'inline'")
    if not isinstance(placeholder, str):
        raise TypeError("placeholder debe ser str")
    if not isinstance(show_copy_button, bool):
        raise TypeError("show_copy_button debe ser bool")
    if not isinstance(show_status_bar, bool):
        raise TypeError("show_status_bar debe ser bool")
    normalized_diff = _normalize_diff(diff)

    blocks = _normalize_blocks(initial_blocks)
    renderer_bundle = _ASSET_DIR / "renderers.bundle.js"
    if not renderer_bundle.is_file():
        raise RuntimeError(
            "Falta el bundle de renderizadores: ejecuta npm install y npm run build "
            "en markdown_editor\\frontend"
        )
    editor = create_component(
        name="markdown_block_editor",
        html=(_ASSET_DIR / "editor.html").read_text(encoding="utf-8"),
        css=(_ASSET_DIR / "editor.css").read_text(encoding="utf-8"),
        js=(
            renderer_bundle.read_text(encoding="utf-8")
            + "\n"
            + (_ASSET_DIR / "editor.js").read_text(encoding="utf-8")
        ),
        isolate_styles=False,
    )
    state = editor(
        key=key,
        data={
            "blocks": blocks,
            "revision": revision,
            "mode": mode,
            "save_mode": save_mode,
            "only_view": only_view,
            "debug_blocks": debug_blocks,
            "height": height,
            "diff": normalized_diff,
            "editor_modes": list(editor_modes),
            "review_modes": list(review_modes),
            "review_layouts": list(review_layouts),
            "block_diff_style": block_diff_style,
            "placeholder": placeholder,
            "show_copy_button": show_copy_button,
            "show_status_bar": show_status_bar,
            "toolbar_sections": list(toolbar_sections),
        },
        width="stretch",
        height=height if height is not None else 760,
    ).get("value")
    return _document_from_state(state, blocks, mode=mode, save_mode=save_mode)


__all__ = ["st_markdown_block_editor"]
