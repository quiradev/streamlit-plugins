import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "__init__.py"
)


@pytest.fixture
def editor_module(monkeypatch):
    spec = importlib.util.spec_from_file_location("markdown_editor_under_test", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    component = Mock(return_value={})
    monkeypatch.setitem(module.__dict__, "create_component", Mock(return_value=component))
    return module, component


@pytest.mark.parametrize("height", [None, 240, 760, "stretch", "content"])
def test_height_and_debug_are_passed_to_component(editor_module, height):
    module, component = editor_module
    blocks = [{"id": "list", "markdown": "5. Parent\n    - Child"}]

    result = module.st_markdown_block_editor(
        blocks, key="test", height=height, debug_blocks=True
    )

    assert component.call_args.kwargs["height"] == (760 if height is None else height)
    assert component.call_args.kwargs["data"]["height"] == height
    assert component.call_args.kwargs["data"]["debug_blocks"] is True
    assert result["markdown"] == blocks[0]["markdown"]


@pytest.mark.parametrize(
    "height,error",
    [(239, ValueError), (-1, ValueError), (True, TypeError), (760.0, TypeError),
     ("full", ValueError), ([], TypeError)],
)
def test_invalid_height_is_rejected_before_rendering(editor_module, height, error):
    module, component = editor_module

    with pytest.raises(error, match="height"):
        module.st_markdown_block_editor([], key="test", height=height)

    component.assert_not_called()


@pytest.mark.parametrize("debug", [1, None, "true"])
def test_debug_requires_a_boolean(editor_module, debug):
    module, component = editor_module

    with pytest.raises(TypeError, match="debug_blocks"):
        module.st_markdown_block_editor([], key="test", debug_blocks=debug)

    component.assert_not_called()


def test_readonly_diff_and_debug_do_not_change_source(editor_module):
    module, component = editor_module
    diff = {"before": "# Before", "after": "# After"}

    result = module.st_markdown_block_editor(
        [{"id": "body", "markdown": "Original"}],
        key="test",
        only_view=True,
        diff=diff,
        debug_blocks=True,
    )

    assert component.call_args.kwargs["data"]["diff"] == diff
    assert component.call_args.kwargs["data"]["only_view"] is True
    assert result["markdown"] == "Original"


@pytest.mark.parametrize("visible", [True, False])
def test_status_bar_visibility_is_passed_to_component(editor_module, visible):
    module, component = editor_module
    module.st_markdown_block_editor([], key="test", show_status_bar=visible)
    assert component.call_args.kwargs["data"]["show_status_bar"] is visible


def test_status_bar_is_enabled_by_default(editor_module):
    module, component = editor_module
    module.st_markdown_block_editor([], key="test")
    assert component.call_args.kwargs["data"]["show_status_bar"] is True


@pytest.mark.parametrize("visible", [None, 1, "false"])
def test_status_bar_requires_a_boolean(editor_module, visible):
    module, component = editor_module
    with pytest.raises(TypeError, match="show_status_bar"):
        module.st_markdown_block_editor([], key="test", show_status_bar=visible)
    component.assert_not_called()
