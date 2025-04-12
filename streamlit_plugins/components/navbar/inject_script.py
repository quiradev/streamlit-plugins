import json

import requests
import streamlit.components.v1 as components

from .config import _RELEASE, build_path, dev_url


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
    escaped_content = content.replace("`", r"\`").replace("${", r"\${")
    components.html(
        f"""<script>
frameElement.parentElement.style.display = 'none';
if (!window.parent.NavbarCOI_injected) {{
    window.parent.NavbarCOI_injected = true;
    var script = window.parent.document.createElement('script');
    script.text = `{escaped_content}`;
    script.type = 'text/javascript';
    window.parent.document.head.appendChild(script);
}}
</script>""",
        height=0,
        width=0,
    )


def instantiate_crossorigin_interface(component_name: str, key: str, is_navigation: bool, default_page_id: str, position_mode: str, sticky_nav: bool):
    """Instantiate the CrossOriginInterface in the parent scope that responds to messages for key."""
    components.html(
        f"""<script>
frameElement.parentElement.style.display = 'none';
window.parent.navbarCOI = new window.parent.instantiateNavbarCOI('{component_name}', '{key}', {json.dumps(is_navigation)}, '{default_page_id}', '{position_mode}', {json.dumps(sticky_nav)});
</script>""",
        height=0,
        width=0,
    )

def apply_styles(key: str, custom_styles: str):
    if _RELEASE:
        interface_script_path = build_path / "st-styles.css"
        with open(interface_script_path) as reader:
            content = reader.read()
    else:
        # Load the script from dev_url
        response = requests.get(f"{dev_url}/st-styles.css")
        content = response.text
        pass

    components.html(
        f"""<script>
    window.parent.navbarCOI.applyNavbarStyles('{key}', `{content}`, {custom_styles})
    </script>""",
        height=0,
        width=0,
    )