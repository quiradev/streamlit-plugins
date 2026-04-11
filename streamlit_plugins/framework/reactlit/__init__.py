"""
Reactlit - Reactive Fragment Framework for Streamlit

Framework que permite crear componentes reactivos (fragmentos) que
se actualizan automáticamente cuando sus dependencias cambian.

Características:
- Fragmentos reactivos con detección de cambios
- Grafo de dependencias entre componentes
- Prevención de ciclos infinitos
- Cascadas automáticas de reruns
- Observación de state compartido

Uso básico:

    from streamlit_plugins.framework.reactlit import reactive_fragment

    @reactive_fragment(
        dependencies=['user_id', 'filters'],
        watch_params=True
    )
    def my_panel(user_id, filters=None):
        st.write(f"Data for {user_id}")

    @reactive_fragment(dependencies=['my_panel'])
    def dependent_panel():
        st.write("This updates when my_panel changes")
"""

from .reactive import (
    # Decorators
    reactive_fragment,
    # Registration
    register_dependency,
    register_dependencies,
    # Query & Introspection
    get_fragment_metadata,
    get_all_fragments,
    get_dependency_chain,
    has_dependency_cycle,
    # Utilities
    get_fragment_state,
    set_fragment_dirty,
    enqueue_fragment_rerun,
    manually_trigger_rerun_cascade,
    # Debugging
    debug_dependency_graph,
    reset_reactive_state,
    # Data Models
    FragmentMetadata,
    DependencyGraph,
)

__all__ = [
    # Decorators
    "reactive_fragment",
    # Registration
    "register_dependency",
    "register_dependencies",
    # Query & Introspection
    "get_fragment_metadata",
    "get_all_fragments",
    "get_dependency_chain",
    "has_dependency_cycle",
    # Utilities
    "get_fragment_state",
    "set_fragment_dirty",
    "enqueue_fragment_rerun",
    "manually_trigger_rerun_cascade",
    # Debugging
    "debug_dependency_graph",
    "reset_reactive_state",
    # Data Models
    "FragmentMetadata",
    "DependencyGraph",
]

__version__ = "0.1.0"

