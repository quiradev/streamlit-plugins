import os

import requests
import streamlit.components.v1 as components

from .config import dev_url, build_path, _RELEASE


def inject_crossorigin_interface():
    """Inject the CrossOriginInterface script into the parent scope."""

    # Load text content of COI
    if _RELEASE:
        interface_script_path = build_path / "CrossOriginInterface.js"
        with open(interface_script_path) as reader:
            content = reader.read()
    else:
        # Load the script from dev_url
        response = requests.get(f"{dev_url}/CrossOriginInterface.js")
        content = response.text
        pass

    # Run COI content in parent
    # This works because streamlit.components.v1.html() creates an iframe from same domain as the parent scope
    # Same domain can bypass sandbox restrictions to create an interface for cross-origin iframes
    # This allows custom components to interact with parent scope
    components.html(
        f"""<script>
frameElement.parentElement.style.display = 'none';
if (!window.parent.COI_injected) {{
    window.parent.COI_injected = true;
    var script = window.parent.document.createElement('script');
    script.text = `{content}`;
    script.type = 'text/javascript';
    window.parent.document.head.appendChild(script);
}}
</script>""",
        height=0,
        width=0,
    )


def instantiate_crossorigin_interface(key):
    """Instantiate the CrossOriginInterface in the parent scope that responds to messages for key."""
    components.html(
        f"""<script>
frameElement.parentElement.style.display = 'none';
window.parent.instantiateCrossOriginInterface('{key}');
</script>""",
        height=0,
        width=0,
    )