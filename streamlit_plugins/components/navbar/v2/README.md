# Navbar V2: local development

V2 is a Streamlit custom component and needs Streamlit 1.51 or newer. Streamlit discovers it through installed package metadata, so importing the checkout without installing the package is not sufficient.

From the repository root, install the navbar package from the checkout. Use the same interpreter that will run Streamlit. Do not install `navbar/v2`: the root `pyproject.toml` defines the Python distribution and its V2 component manifest; `v2/pyproject.toml` is component metadata, not a separate pip package.

```powershell
python -m pip install "streamlit>=1.51"
python -m pip install --force-reinstall --no-deps .\streamlit_plugins\components\navbar
```

The committed files in `v2/frontend/build` are used directly; no frontend build is needed to try the component. If you change frontend sources, rebuild and reinstall the package so the new assets and manifest are installed:

```powershell
docker compose -f .\streamlit_plugins\components\docker-compose.yml run --build --rm navbar_v2 npm run build
python -m pip install --force-reinstall --no-deps .\streamlit_plugins\components\navbar
```

Commit the generated `frontend/build` files with the source changes. The release workflow packages these prebuilt assets and does not run the frontend build.

If `importlib.metadata.distributions()` still lists the navbar after uninstalling it, remove the stale build metadata from the repository root; `pip uninstall` does not remove it:

```powershell
Remove-Item -Recurse -Force .\streamlit_component_navbar.egg-info
```

Create an app, for example `navbar_v2_local.py` in the repository root:

```python
import streamlit as st

from streamlit_plugins.components.navbar import st_navbar_v2

selection = st_navbar_v2(
    menu_definition=[{"id": "settings", "label": "Settings"}],
    home_definition={"id": "home", "label": "Home"},
    position_mode="static",
)
st.write(f"Selected: {selection}")
```

Run it using the same Python environment where the package was installed:

```powershell
streamlit run .\navbar_v2_local.py
```
