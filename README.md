# Streamlit Plugins

Components and frameworks to extend Streamlit's capabilities with advanced features and customizations.

![Demo Multipage with Navbar](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/navbar_change_theme.gif)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
   - [Frameworks](#frameworks)
   - [Components](#components)
3. [Usage](#usage)
   - [Quickstart](#quickstart)
   - [Example Code](#example-code)
4. [Roadmap](#roadmap)
5. [Contributing](#contributing)
6. [License](#license)

---

## Introduction

Welcome to **Streamlit Plugins**, a collection of tools designed to enhance your Streamlit apps with features like:
- A customizable **Navbar** with multiple positioning options (including lateral mode!).
- A **Loader** for better user feedback.
- Advanced integrations like **LabelStudio** and **SnakeViz**.

---

## Features

### Frameworks

#### Multilit (Inherits from Hydralit)
This is a fork of [Hydralit](https://github.com/TangleSpace/hydralit) with updated compatibility for the latest Streamlit version.

- Improved interface and user experience.
- Respects Streamlit's active theme, with support for user overrides.
- Future plans to integrate native Streamlit multipage functionality.

**Key Features:**
- Built-in buttons or programmatic page navigation.

![Change Page with button](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/demo2.gif)

---

### Components

#### Navbar (Sidebar, Topbar, and Under Streamlit Header)

> [More info](/streamlit_plugins/components/navbar/README.md)

![Navbar Component](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/navbar_position_modes.gif)

A versatile navbar component with support for:
- Native Streamlit multipage apps.
- Multilit framework.
- Multiple positions: top, under, and side.

**Responsive and Customizable:**
- Adjust themes and configurations dynamically.

#### Example: Multipage App with Native Streamlit Navbar
```python
st.set_page_config(layout="wide")
# Example Sidebar
with st.sidebar:
    st.radio("Navbar Position", ["top", "under", "side"])
    st.checkbox("Sticky Navbar")
# Example Navbar Integration
from streamlit_plugins.components.navbar import st_navbar
st_navbar(
    menu_definition=[{"name": "Home", "icon": "🏠", "page": "home.py"}],
    position_mode="top"
)
```

#### Loader (Inherit from Hydralit Components)

Enhance user experience with loaders for transitions and long-running tasks.

#### AnnotatedText (Inspired by SpaCy Annotated Text)

> [More info](/streamlit_plugins/components/annotated_text/README.md)

Display annotated text inline with your app for NLP tasks.

#### LabelStudio (In Development)

> [More info](/streamlit_plugins/components/label_studio/README.md)

Adapter for integrating LabelStudio into Streamlit for NER and annotation tasks.

#### SnakeViz

Visualize and analyze bottlenecks in your Python code directly within Streamlit.

---

## Usage

### Quickstart
1. Install the package:
   ```bash
   pip install streamlit-plugins
   ```
2. Import and use components in your Streamlit app.

### Example Code
See the [examples folder](examples/) for detailed implementations and usage scenarios.

---

## Roadmap

### Framework: Multilit
- [ ] Use native streamlit multipage system

### Compontent: Navbar
- [x] Add Navbar with lateral mode.
- [x] Support for dynamic theme changes.
- [ ] Add more CSS customization options.
- [ ] Improve documentation and examples.

### Compontent: LabelStudio
- [ ] Expand LabelStudio integration.

---

## Contributing

We welcome contributions! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

⭐ **If you find this project useful, please consider giving it a star!**
