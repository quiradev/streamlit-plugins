"""
Reactive Fragment Framework for Streamlit
==========================================

Sistema reactivo para fragmentos en Streamlit que permite:
- Definir fragmentos con dependencias (como componentes React)
- Detectar cambios en dependencias automáticamente
- Ejecutar cascadas de reruns manteniendo el árbol de dependencias
- Evitar loops infinitos y manejar ciclos
- Mantener estado compartido via session_state
- Controlar delta paths para renderizado en el mismo sitio

Uso:
    @reactive_fragment(
        dependencies=['input_filter', 'user_settings'],
        dependents=['fragment_b', 'fragment_c']
    )
    def my_fragment():
        st.write("Mi componente reactivo")
"""

import functools
import hashlib
import inspect
import typing
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Set

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx, RerunData


# =============================================================================
# 🏗️ CORE DATA STRUCTURES
# =============================================================================

@dataclass
class FragmentMetadata:
    """Metadata para un fragmento reactivo"""
    name: str
    func: Callable
    dependencies: Set[str] = field(default_factory=set)  # Qué state keys observa
    dependents: Set[str] = field(default_factory=set)  # Qué otros fragmentos dependen de este
    param_watchers: dict[str, Any] = field(default_factory=dict)  # {param_name: last_value}
    delta_path: Optional[str] = None
    fragment_id: Optional[str] = None
    is_dirty: bool = False


@dataclass
class DependencyGraph:
    """Grafo de dependencias entre fragmentos"""
    fragments: dict[str, FragmentMetadata] = field(default_factory=dict)
    rerun_queue: list[str] = field(default_factory=list)
    visited_in_cycle_check: Set[str] = field(default_factory=set)

    def add_fragment(self, metadata: FragmentMetadata) -> None:
        """Registra un fragmento en el grafo"""
        self.fragments[metadata.name] = metadata

    def add_dependency(self, fragment: str, depends_on: str) -> None:
        """Añade una dependencia: fragment depende de depends_on"""
        if fragment in self.fragments and depends_on in self.fragments:
            self.fragments[fragment].dependencies.add(depends_on)
            self.fragments[depends_on].dependents.add(fragment)

    def get_dependents_chain(self, fragment_name: str) -> Set[str]:
        """Retorna todos los fragmentos que dependen (transitivamente) de este"""
        visited = set()
        stack = [fragment_name]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            if current in self.fragments:
                for dep in self.fragments[current].dependents:
                    if dep not in visited:
                        stack.append(dep)

        visited.discard(fragment_name)
        return visited

    def has_cycle(self, start: str, current: str = None, visited: Set[str] = None) -> bool:
        """Detecta ciclos desde start"""
        if current is None:
            current = start
            visited = set()

        if current in visited:
            return current == start

        visited.add(current)

        if current in self.fragments:
            for dependent in self.fragments[current].dependents:
                if self.has_cycle(start, dependent, visited.copy()):
                    return True

        return False


# =============================================================================
# 🎛️ GLOBAL STATE MANAGEMENT
# =============================================================================

_GLOBAL_REGISTRY: dict[str, FragmentMetadata] = {}
_GLOBAL_GRAPH: DependencyGraph = DependencyGraph()
_FRAGMENT_ID_TO_NAME: dict[str, str] = {}


def _get_session_graph() -> dict:
    """Obtiene o crea el grafo de dependencias en session_state"""
    if '_reactive_graph_state' not in st.session_state:
        st.session_state._reactive_graph_state = {
            'rerun_queue': [],
            'executing': set(),
            'last_params': {},
            'fragment_ids': {},
        }
    return st.session_state._reactive_graph_state


def _get_or_init_fragment_state(fragment_name: str) -> dict:
    """Inicializa estado para un fragmento específico"""
    state_key = f'_fragment_state_{fragment_name}'
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            'params': {},
            'is_dirty': False,
            'last_rendered_params': {},
        }
    return st.session_state[state_key]


# =============================================================================
# 📍 FRAGMENT TRACKING
# =============================================================================

def _get_fragment_delta_path() -> str:
    """Obtiene el delta path actual del fragmento"""
    ctx = get_script_run_ctx()
    if ctx is None:
        return ""

    # En un fragmento, el delta path es el stack de contenedores donde se define
    dg_stack = getattr(ctx, 'dg', None)
    if dg_stack and hasattr(dg_stack, '_root') and hasattr(dg_stack._root, '_delta_path'):
        return str(dg_stack._root._delta_path)

    return ""


def _get_current_fragment_id() -> Optional[str]:
    """Obtiene el ID del fragmento actual de ejecución"""
    ctx = get_script_run_ctx()
    if ctx is None:
        return None

    # El fragment_id se asigna durante la ejecución del fragmento
    return getattr(ctx, 'current_fragment_id', None)


# =============================================================================
# 🔄 CHANGE DETECTION
# =============================================================================

def _compute_param_hash(params: dict) -> str:
    """Calcula un hash de los parámetros para detectar cambios"""
    try:
        param_str = str(sorted(params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()
    except Exception:
        return "unknown"


def _detect_param_changes(
    fragment_name: str,
    current_params: dict[str, Any],
) -> tuple[bool, Set[str]]:
    """
    Detecta si los parámetros han cambiado.
    Retorna: (hay_cambios, parámetros_que_cambiaron)
    """
    state = _get_or_init_fragment_state(fragment_name)
    last_params = state.get('last_rendered_params', {})

    changed_params = set()

    for key, new_value in current_params.items():
        old_value = last_params.get(key)
        if old_value != new_value:
            changed_params.add(key)

    # También detectar si desaparecieron parámetros
    for key in last_params:
        if key not in current_params:
            changed_params.add(key)

    has_changes = len(changed_params) > 0

    return has_changes, changed_params


def _mark_dependents_dirty(fragment_name: str, graph: DependencyGraph) -> None:
    """Marca como dirty todos los fragmentos que dependen de este"""
    dependents = graph.get_dependents_chain(fragment_name)

    for dependent in dependents:
        state = _get_or_init_fragment_state(dependent)
        state['is_dirty'] = True


def _detect_complex_cycles(graph: DependencyGraph) -> tuple[bool, Set[str]]:
    """
    Detecta ciclos complejos en el grafo.
    Retorna: (hay_ciclos, fragmentos_con_ciclos)
    """
    fragments_with_cycles = set()
    
    for fragment_name in graph.fragments.keys():
        if graph.has_cycle(fragment_name):
            fragments_with_cycles.add(fragment_name)
    
    return len(fragments_with_cycles) > 0, fragments_with_cycles


def _trigger_global_rerun(graph: DependencyGraph) -> bool:
    """
    Dispara un rerun global limpiando todo.
    Si ya se ha disparado un global rerun, lanza error.
    Retorna: True si se puede hacer, False si hay bug
    """
    graph_state = _get_session_graph()
    
    # Si ya se disparó un global rerun, es un bug
    if graph_state['global_rerun_triggered']:
        st.error(
            "🚨 **CRITICAL BUG DETECTED**: "
            "Multiple global reruns attempted. "
            "State is inconsistent. Please refresh the page."
        )
        st.session_state._reactive_framework_log = (
            st.session_state.get('_reactive_framework_log', []) +
            ["[ERROR] Multiple global reruns - state corrupted"]
        )
        return False
    
    # Marca que se va a hacer global rerun
    graph_state['global_rerun_triggered'] = True
    graph_state['global_rerun_count'] += 1
    
    st.session_state._reactive_framework_log = (
        st.session_state.get('_reactive_framework_log', []) +
        [f"[GLOBAL_RERUN] #{graph_state['global_rerun_count']} - Full reset triggered"]
    )
    
    return True


def _reset_reactive_session_state() -> None:
    """
    Reseta el estado reactivo de forma segura.
    Se llama cuando se detectan ciclos complejos.
    """
    # Limpia todo excepto los datos críticos
    if '_reactive_graph_state' in st.session_state:
        old_count = st.session_state._reactive_graph_state.get('global_rerun_count', 0)
        del st.session_state._reactive_graph_state
    
    # Limpia estados de fragmentos individuales
    for key in list(st.session_state.keys()):
        if key.startswith('_fragment_state_'):
            del st.session_state[key]
    
    # Reinicializa con el contador preservado
    graph_state = _get_session_graph()
    graph_state['global_rerun_count'] = old_count


# =============================================================================
# 🚀 RERUN MANAGEMENT
# =============================================================================

def _queue_fragment_rerun(fragment_name: str, reason: str = "") -> None:
    """Encola un fragmento para rerun"""
    graph_state = _get_session_graph()

    if fragment_name not in graph_state['rerun_queue']:
        graph_state['rerun_queue'].append(fragment_name)
        st.session_state._reactive_framework_log = (
            st.session_state.get('_reactive_framework_log', []) +
            [f"[QUEUE] {fragment_name} {reason}"]
        )


def _process_rerun_queue() -> None:
    """Procesa la cola de fragmentos que necesitan rerun"""
    graph_state = _get_session_graph()

    while graph_state['rerun_queue']:
        fragment_name = graph_state['rerun_queue'].pop(0)

        if fragment_name in graph_state['executing']:
            continue  # Evita recursión infinita

        if fragment_name not in _GLOBAL_REGISTRY:
            continue

        graph_state['executing'].add(fragment_name)

        # Dispara rerun para este fragmento específico
        _trigger_fragment_rerun(fragment_name)

        graph_state['executing'].discard(fragment_name)


def _trigger_fragment_rerun(fragment_name: str) -> bool:
    """
    Dispara rerun de un fragmento específico.
    Retorna True si se pudo, False si no existe.
    """
    ctx = get_script_run_ctx()
    if ctx is None:
        return False

    fragment_storage = getattr(ctx, 'fragment_storage', None)
    if fragment_storage is None:
        return False

    # Busca el fragmento por nombre
    for fragment_id, fragment_wrapper in fragment_storage.fragments.items():
        # Intenta acceder al nombre de la función original
        func = getattr(fragment_wrapper, '__wrapped__', fragment_wrapper)
        if hasattr(func, '__name__') and func.__name__ == fragment_name:
            try:
                rerun_data = RerunData(
                    fragment_id=fragment_id,
                    widget_states=None,
                    page_script_hash=ctx.page_script_hash,
                )
                ctx.session.request_rerun(rerun_data)
                return True
            except Exception:
                pass

    return False


# =============================================================================
# 🎨 REACTIVE FRAGMENT DECORATOR
# =============================================================================

def reactive_fragment(
    dependencies: Optional[list[str]] = None,
    dependents: Optional[list[str]] = None,
    watch_params: bool = True,
    prevent_cycles: bool = True,
):
    """
    Decorador para crear fragmentos reactivos.

    Args:
        dependencies: Lista de nombres de fragmentos o keys de session_state que observa
        dependents: Lista de nombres de fragmentos que dependen de este
        watch_params: Si True, observa cambios en parámetros de la función
        prevent_cycles: Si True, evita ejecutar si detecta ciclos

    Ejemplo:
        @reactive_fragment(
            dependencies=['user_id', 'filter_values'],
            dependents=['stats_panel', 'chart_panel']
        )
        def data_loader(user_id, filters=None):
            st.write(f"Loading data for {user_id}")
    """
    dep_list = set(dependencies or [])
    dep_names = set(dependents or [])

    def decorator(func: Callable) -> Callable:
        fragment_name = func.__name__

        # Registra metadatos
        metadata = FragmentMetadata(
            name=fragment_name,
            func=func,
            dependencies=dep_list,
            dependents=dep_names,
        )

        _GLOBAL_REGISTRY[fragment_name] = metadata
        _GLOBAL_GRAPH.add_fragment(metadata)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ctx = get_script_run_ctx()

            # Obtiene estado de la sesión
            graph_state = _get_session_graph()
            frag_state = _get_or_init_fragment_state(fragment_name)
            
            # VERIFICACIÓN 1: Si hay un global rerun en progreso, no ejecutar
            if graph_state['global_rerun_triggered']:
                st.warning(
                    "⚠️ Global rerun in progress - waiting for page refresh"
                )
                return None
            
            # VERIFICACIÓN 2: Detectar ciclos complejos en el grafo
            has_cycles, cycle_fragments = _detect_complex_cycles(_GLOBAL_GRAPH)
            
            if has_cycles:
                # Registra ciclos encontrados
                if not graph_state['cycle_detected']:
                    graph_state['cycle_detected'] = True
                    graph_state['cycle_fragments'] = cycle_fragments
                    
                    st.session_state._reactive_framework_log = (
                        st.session_state.get('_reactive_framework_log', []) +
                        [f"[CYCLE_DETECTED] Fragments: {cycle_fragments}"]
                    )
                    
                    # Si el fragmento actual está en ciclo, hace global rerun
                    if fragment_name in cycle_fragments:
                        if _trigger_global_rerun(_GLOBAL_GRAPH):
                            st.warning(
                                f"🔄 Complex cycle detected in '{fragment_name}'. "
                                "Performing full reset. Please refresh the page."
                            )
                            _reset_reactive_session_state()
                            st.rerun()
                        else:
                            # Bug detectado - múltiples global reruns
                            return None
            
            # Actualiza delta path del fragmento
            metadata.delta_path = _get_fragment_delta_path()
            metadata.fragment_id = _get_current_fragment_id()


            # Prepara parámetros combinados
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            current_params = dict(bound.arguments)

            # Detecta cambios en parámetros
            has_param_changes, changed_params = _detect_param_changes(
                fragment_name,
                current_params
            )

            # Actualiza estado de parámetros
            frag_state['params'] = current_params
            frag_state['last_rendered_params'] = current_params.copy()

            # Si hay cambios en parámetros observados, marca dependientes como dirty
            if has_param_changes and watch_params:
                st.session_state._reactive_framework_log = (
                    st.session_state.get('_reactive_framework_log', []) +
                    [f"[CHANGE] {fragment_name}: {changed_params}"]
                )
                _mark_dependents_dirty(fragment_name, _GLOBAL_GRAPH)

            # Ejecuta el fragmento original
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                st.error(f"Error en fragmento {fragment_name}: {str(e)}")
                result = None

            # Procesa fragmentos pendientes de rerun
            if graph_state['rerun_queue'] and not graph_state['executing']:
                # En la siguiente iteración, procesaremos la cola
                pass

            return result

        return st.fragment(wrapper)

    return decorator


# =============================================================================
# 🔗 DEPENDENCY REGISTRATION
# =============================================================================

def register_dependency(fragment: str, depends_on: str) -> None:
    """
    Registra una dependencia entre dos fragmentos.

    Args:
        fragment: Nombre del fragmento que depende
        depends_on: Nombre del fragmento del que depende
    """
    _GLOBAL_GRAPH.add_dependency(fragment, depends_on)


def register_dependencies(fragment: str, dependencies: list[str]) -> None:
    """Registra múltiples dependencias"""
    for dep in dependencies:
        register_dependency(fragment, dep)


# =============================================================================
# 🔍 QUERY & INTROSPECTION
# =============================================================================

def get_fragment_metadata(fragment_name: str) -> Optional[FragmentMetadata]:
    """Obtiene metadatos de un fragmento registrado"""
    return _GLOBAL_REGISTRY.get(fragment_name)


def get_all_fragments() -> dict[str, FragmentMetadata]:
    """Retorna todos los fragmentos registrados"""
    return _GLOBAL_REGISTRY.copy()


def get_dependency_chain(fragment_name: str) -> Set[str]:
    """Obtiene la cadena completa de dependientes de un fragmento"""
    return _GLOBAL_GRAPH.get_dependents_chain(fragment_name)


def has_dependency_cycle(fragment_name: str) -> bool:
    """Verifica si existe un ciclo en las dependencias"""
    return _GLOBAL_GRAPH.has_cycle(fragment_name)


# =============================================================================
# 📊 DEBUGGING & MONITORING
# =============================================================================

def debug_dependency_graph() -> None:
    """Muestra el grafo de dependencias en debug"""
    with st.expander("🔍 Debug: Dependency Graph"):
        st.write("**Fragmentos registrados:**")
        for name, metadata in _GLOBAL_REGISTRY.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{name}**")
            with col2:
                st.write(f"Depende de: {metadata.dependencies or 'Nada'}")
            with col3:
                st.write(f"Lo usan: {metadata.dependents or 'Nada'}")

        st.write("\n**Cola de reruns:**")
        graph_state = _get_session_graph()
        st.write(graph_state['rerun_queue'] or "Vacía")

        st.write("\n**Logs:**")
        logs = st.session_state.get('_reactive_framework_log', [])
        for log in logs[-20:]:  # Últimos 20 logs
            st.text(log)


def reset_reactive_state() -> None:
    """
    Limpia el estado reactivo (útil para testing).
    Preserva información de global reruns para debugging.
    """
    # Guarda contador de global reruns antes de limpiar
    global_rerun_count = 0
    if '_reactive_graph_state' in st.session_state:
        global_rerun_count = st.session_state._reactive_graph_state.get('global_rerun_count', 0)
        del st.session_state._reactive_graph_state
    
    # Limpia estados de fragmentos
    for key in list(st.session_state.keys()):
        if key.startswith('_fragment_state_'):
            del st.session_state[key]
    
    # Reinicializa con contador preservado
    graph_state = _get_session_graph()
    graph_state['global_rerun_count'] = global_rerun_count
    
    # Limpia logs si es necesario
    if '_reactive_framework_log' in st.session_state:
        del st.session_state._reactive_framework_log


# =============================================================================
# 🧪 UTILITIES FOR ADVANCED USAGE
# =============================================================================

def get_fragment_state(fragment_name: str) -> dict:
    """Obtiene el estado actual de un fragmento"""
    return _get_or_init_fragment_state(fragment_name).copy()


def set_fragment_dirty(fragment_name: str, dirty: bool = True) -> None:
    """Marca manualmente un fragmento como dirty"""
    state = _get_or_init_fragment_state(fragment_name)
    state['is_dirty'] = dirty


def enqueue_fragment_rerun(fragment_name: str, reason: str = "") -> None:
    """Encola manualmente un fragmento para rerun"""
    _queue_fragment_rerun(fragment_name, reason)


def manually_trigger_rerun_cascade(root_fragment: str) -> None:
    """Dispara manualmente un cascade de reruns desde un fragmento raíz"""
    chain = get_dependency_chain(root_fragment)
    for fragment_name in chain:
        enqueue_fragment_rerun(fragment_name, "cascade from " + root_fragment)

