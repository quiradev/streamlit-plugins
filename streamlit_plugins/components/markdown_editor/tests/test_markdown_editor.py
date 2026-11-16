import importlib.util
from contextlib import nullcontext
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


def test_raw_markdown_is_passed_to_frontend_and_preserved(editor_module):
    module, component = editor_module
    markdown = "# Título\n\nTexto **editable**."

    result = module.st_markdown_block_editor(markdown, key="test")

    assert component.call_args.kwargs["data"]["initial_markdown"] == markdown
    assert result["markdown"] == markdown


def test_preview_wrapper_restores_autosaved_blocks_and_forwards_options(editor_module, monkeypatch):
    module, _ = editor_module

    class FakeUI:
        session_state = {}
        rendered_markdown = []
        containers = []
        warnings = []

        def container(self, **kwargs):
            self.containers.append(kwargs)
            return nullcontext()

        def warning(self, message):
            self.warnings.append(message)

        def toggle(self, label, *, key):
            return self.session_state.get(key, False)

        def markdown(self, markdown):
            self.rendered_markdown.append(markdown)

    ui = FakeUI()
    monkeypatch.setattr(module, "st", ui)
    editor = Mock(return_value={
        "blocks": [{"id": "block-0", "markdown": "Edited"}],
        "markdown": "Edited",
        "mode": "visual",
        "save_mode": "auto",
    })
    monkeypatch.setattr(module, "st_markdown_block_editor", editor)

    result = module.st_markdown_editor_with_preview(
        "Original", key="test", height=600, mode="visual"
    )
    assert result["markdown"] == "Edited"
    assert editor.call_args.kwargs["height"] == 600
    assert ui.containers[-1] == {
        "horizontal": True,
        "horizontal_alignment": "right",
        "vertical_alignment": "center",
    }
    assert ui.warnings == []

    ui.session_state["test__preview_toggle"] = True
    module.st_markdown_editor_with_preview("Original", key="test", height=600)
    assert ui.rendered_markdown == ["Edited"]

    ui.session_state["test__preview_toggle"] = False
    module.st_markdown_editor_with_preview("Original", key="test", height=600)
    assert editor.call_args.args[0] == "Edited"
    assert editor.call_args.kwargs["revision"] == 1

    module.st_markdown_editor_with_preview(
        "Original", key="bottom", toggle_position="bottom_left"
    )
    assert ui.containers[-1] == {
        "horizontal": True,
        "horizontal_alignment": "left",
        "vertical_alignment": "center",
    }

    module.st_markdown_editor_with_preview(
        "Original", key="manual-save", save_mode="button"
    )
    assert ui.warnings == [
        "Los cambios sin guardar se perderán al mostrar la vista previa."
    ]


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


def test_editor_customization_is_passed_to_frontend(editor_module):
    module, component = editor_module
    config = {"theme": "base", "themeVariables": {"primaryColor": "#ff0000"}}
    styles = {"th": {"background-color": "#eeeeee"}, "td": {"padding": "12px"}}
    module.st_markdown_block_editor(
        [], key="test", allowed_block_types=["paragraph", "h2"],
        autosave_delay=800, mermaid_config=config, table_styles=styles,
        mode="visual", editor_modes=["visual"], reorder_mode="buttons",
    )
    data = component.call_args.kwargs["data"]
    assert data["allowed_block_types"] == ["paragraph", "h2"]
    assert data["autosave_delay"] == 800
    assert data["mermaid_config"] == config
    assert data["table_styles"] == styles
    assert data["editor_modes"] == ["visual"]
    assert data["reorder_mode"] == "buttons"


def test_autosave_default_is_defined_in_python(editor_module):
    module, component = editor_module
    module.st_markdown_block_editor([], key="test")
    assert component.call_args.kwargs["data"]["autosave_delay"] == 500
    assert component.call_args.kwargs["data"]["reorder_mode"] == "drag_buttons"


@pytest.mark.parametrize(
    "options,error",
    [
        ({"allowed_block_types": []}, ValueError),
        ({"allowed_block_types": ["heading"]}, ValueError),
        ({"allowed_block_types": ["h2", "h2"]}, ValueError),
        ({"allowed_block_types": "paragraph"}, TypeError),
        ({"reorder_mode": "unknown"}, ValueError),
        ({"reorder_mode": None}, TypeError),
        ({"autosave_delay": True}, TypeError),
        ({"autosave_delay": 0.5}, TypeError),
        ({"autosave_delay": -1}, ValueError),
        ({"autosave_delay": 2_147_483_648}, ValueError),
        ({"mermaid_config": []}, TypeError),
        ({"mermaid_config": {"securityLevel": "loose"}}, ValueError),
        ({"mermaid_config": {"theme": "unknown"}}, ValueError),
        ({"mermaid_config": {"fontFamily": 123}}, TypeError),
        ({"mermaid_config": {"themeVariables": {"primaryColor": []}}}, TypeError),
        ({"table_styles": []}, TypeError),
        ({"table_styles": {"body": {}}}, ValueError),
        ({"table_styles": {"td": {"padding": 10}}}, TypeError),
    ],
)
def test_invalid_customization_is_rejected(editor_module, options, error):
    module, component = editor_module
    with pytest.raises(error):
        module.st_markdown_block_editor([], key="test", **options)
    component.assert_not_called()


def test_preview_wrapper_resumes_from_the_last_document_after_an_unmount(editor_module, monkeypatch):
    """Si el llamante desmonta el editor, al volver se recupera lo que había en pantalla."""

    module, _ = editor_module

    class FakeUI:
        def __init__(self):
            self.session_state = {}
            self.containers = []

        def container(self, **kwargs):
            self.containers.append(kwargs)
            return nullcontext()

        def toggle(self, label, *, key):
            return self.session_state.get(key, False)

        def markdown(self, markdown):
            pass

    ui = FakeUI()
    monkeypatch.setattr(module, "st", ui)
    document = {
        "blocks": [{"id": "block-0", "markdown": "Edited"}],
        "markdown": "Edited",
        "mode": "visual",
        "save_mode": "auto",
    }
    editor = Mock(return_value=document)
    monkeypatch.setattr(module, "st_markdown_block_editor", editor)

    module.st_markdown_editor_with_preview("Original", key="test")
    assert editor.call_args.args[0] == "Original"

    # Montado: manda la fuente externa (sus props no cambian entre runs, así el componente no repinta el canvas).
    ui.session_state["test"] = {"value": {"blocks": document["blocks"]}}
    module.st_markdown_editor_with_preview("Original", key="test")
    assert editor.call_args.args[0] == "Original"

    # El llamante dejó de renderizarlo y Streamlit podó el estado del widget: se arranca del último documento.
    ui.session_state.pop("test")
    module.st_markdown_editor_with_preview("Original", key="test")
    assert editor.call_args.args[0] == [{"id": "block-0", "markdown": "Edited"}]


def test_preview_wrapper_can_render_the_editor_without_the_toggle(editor_module, monkeypatch):
    module, _ = editor_module

    class FakeUI:
        def __init__(self):
            self.session_state = {"hidden__preview_toggle": True}
            self.containers = []
            self.rendered_markdown = []

        def container(self, **kwargs):
            self.containers.append(kwargs)
            return nullcontext()

        def toggle(self, label, *, key):
            raise AssertionError("con show_toggle=False no se pinta el toggle")

        def markdown(self, markdown):
            self.rendered_markdown.append(markdown)

    ui = FakeUI()
    monkeypatch.setattr(module, "st", ui)
    editor = Mock(return_value={
        "blocks": [], "markdown": "Edited", "mode": "visual", "save_mode": "auto",
    })
    monkeypatch.setattr(module, "st_markdown_block_editor", editor)

    result = module.st_markdown_editor_with_preview("Original", key="hidden", show_toggle=False)

    assert ui.containers == []
    assert ui.rendered_markdown == []
    assert editor.called
    assert result["markdown"] == "Edited"


@pytest.mark.parametrize("value", [None, 1, "false"])
def test_show_toggle_requires_a_boolean(editor_module, value):
    module, _ = editor_module

    with pytest.raises(TypeError, match="show_toggle"):
        module.st_markdown_editor_with_preview("Original", key="test", show_toggle=value)
