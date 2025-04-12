import json

import streamlit.components.v1 as components

from .entity import ThemeInput
from .config import build_path


def inject_crossorigin_interface():
    """Inject the CrossOriginInterface script into the parent scope."""

    # Load text content of COI
    interface_script_path = build_path / "CrossOriginInterface.js"
    with open(interface_script_path) as reader:
        content = reader.read()

    # Run COI content in parent
    # This works because streamlit.components.v1.html() creates an iframe from same domain as the parent scope
    # Same domain can bypass sandbox restrictions to create an interface for cross-origin iframes
    # This allows custom components to interact with parent scope
    components.html(
        f"""<script>
frameElement.parentElement.style.display = 'none';
if (!window.parent.ThemeChangerCOI_injected) {{
    window.parent.ThemeChangerCOI_injected = true;
    var script = window.parent.document.createElement('script');
    script.text = `{content}`;
    script.type = 'text/javascript';
    window.parent.document.head.appendChild(script);
}}
</script>""",
        height=0,
        width=0,
    )


def change_theme_coi(key, theme_data: ThemeInput):
    theme_data_raw = theme_data.model_dump_json(exclude_none=True)
    components.html(
        f"""<script>
    // frameElement.parentElement.style.display = 'none';
    window.parent.changeThemeWithCOI('{key}', {theme_data_raw});
    </script>""",
        height=0,
        width=0,
    )