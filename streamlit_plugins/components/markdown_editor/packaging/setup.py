import os
from pathlib import Path

from setuptools import setup

COMPONENT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
long_description = (COMPONENT_DIR / "README.md").read_text(encoding="utf-8")
requirements = [
    line.strip()
    for line in (Path(__file__).parent / "requirements.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]
version = (REPOSITORY_ROOT / "VERSION").read_text(encoding="utf-8").strip()

os.chdir(REPOSITORY_ROOT)
setup(
    name="streamlit-component-markdown-editor",
    version=version,
    license="MIT",
    url="https://github.com/quiradev/streamlit-plugins",
    description="Editor Markdown por bloques para Streamlit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Victor Quilon Ranera",
    author_email="v.quilonr@gmail.com",
    packages=[
        "streamlit_plugins.components",
        "streamlit_plugins.components.markdown_editor",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    include_package_data=False,
    package_data={
        "streamlit_plugins.components.markdown_editor": [
            "frontend/build/*.html",
            "frontend/build/*.css",
            "frontend/build/*.js",
            "frontend/build/THIRD_PARTY_LICENSES.txt",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["streamlit", "plugins", "components", "markdown", "editor"],
    options={
        "sdist": {"dist_dir": "./dist/streamlit-plugins-component-markdown-editor"},
        "bdist_wheel": {"dist_dir": "./dist/streamlit-plugins-component-markdown-editor"},
        "build": {"build_base": "./build/streamlit-plugins-component-markdown-editor"},
    },
)
