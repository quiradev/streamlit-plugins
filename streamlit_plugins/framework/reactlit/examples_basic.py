"""
Ejemplo básico: Reactive Framework
===================================

Demuestra:
- Fragmentos reactivos simples
- Dependencias lineales
- Detección de cambios
"""

import streamlit as st
from streamlit_plugins.framework.reactlit.reactive import (
    reactive_fragment,
    enqueue_fragment_rerun,
    debug_dependency_graph,
)


def init_state():
    if 'counter' not in st.session_state:
        st.session_state.counter = 0


@reactive_fragment(watch_params=True)
def fragment_counter_input():
    """Input para el contador"""
    st.subheader("Contador")

    new_val = st.number_input(
        "Valor:",
        value=st.session_state.counter,
        key="counter_input"
    )

    if new_val != st.session_state.counter:
        st.session_state.counter = new_val
        enqueue_fragment_rerun("fragment_counter_display", "counter changed")
        st.rerun(scope="fragment")


@reactive_fragment(
    dependencies=['counter'],
    watch_params=True
)
def fragment_counter_display():
    """Display del contador"""
    st.subheader("Valor Actual")
    st.metric("Contador", st.session_state.counter)


def main():
    st.title("Reactive Fragment - Ejemplo Básico")

    init_state()

    fragment_counter_input()
    fragment_counter_display()

    debug_dependency_graph()


if __name__ == "__main__":
    main()

