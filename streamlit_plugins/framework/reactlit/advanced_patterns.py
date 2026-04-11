"""
Advanced Patterns & Architecture for Reactive Framework
========================================================

Patrones avanzados para construir aplicaciones complejas
con el framework de fragmentos reactivos.
"""

import streamlit as st
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass


# =============================================================================
# 🏗️ ARQUITECTURA: FLUX-LIKE PATTERN
# =============================================================================

@dataclass
class Action:
    """Acción que modifica el estado global"""
    type: str
    payload: Optional[Dict[str, Any]] = None


class ReactiveStore:
    """
    Almacén centralizado similar a Redux/Flux
    para gestionar estado compartido complejo.

    Uso:
        store = ReactiveStore()
        store.define_action('SET_USER', lambda state, user: {**state, user})
        store.dispatch(Action('SET_USER', {'id': 1, 'name': 'John'}))
        store.subscribe('user_changed', my_callback)
    """

    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.reducers: Dict[str, Callable] = {}
        self.subscribers: Dict[str, list] = {}
        self._in_session_state()

    def _in_session_state(self):
        """Persiste el store en session_state"""
        if '_reactive_store' not in st.session_state:
            st.session_state._reactive_store = self

    def define_action(
        self,
        action_type: str,
        reducer: Callable[[Dict, Any], Dict]
    ) -> None:
        """
        Define cómo una acción transforma el estado.

        Args:
            action_type: Nombre único de la acción
            reducer: Función que toma (state, payload) → nuevo state

        Ejemplo:
            def increment_counter(state, amount):
                return {
                    **state,
                    'counter': state.get('counter', 0) + amount
                }

            store.define_action('INCREMENT', increment_counter)
        """
        self.reducers[action_type] = reducer

    def dispatch(self, action: Action) -> None:
        """
        Dispara una acción que modifica el estado.

        Args:
            action: Action con type y payload

        Ejemplo:
            store.dispatch(Action('INCREMENT', {'amount': 5}))
        """
        if action.type not in self.reducers:
            return

        reducer = self.reducers[action.type]
        new_state = reducer(self.state, action.payload)

        # Solo actualiza si cambió
        if new_state != self.state:
            self.state = new_state
            self._notify_subscribers(action.type)

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Se suscribe a cambios de un tipo de acción.

        Args:
            event_type: Tipo de acción a observar
            callback: Función que se llama cuando ocurre

        Ejemplo:
            store.subscribe('INCREMENT', lambda: print("Incremented!"))
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def _notify_subscribers(self, event_type: str) -> None:
        """Notifica a todos los suscriptores de un evento"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback()
                except Exception as e:
                    st.error(f"Error en subscriber: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Accede a un valor del estado"""
        return self.state.get(key, default)

    def select(self, selector: Callable) -> Any:
        """
        Selecciona una parte del estado con una función.

        Ejemplo:
            user = store.select(lambda s: s.get('user'))
            items = store.select(lambda s: s.get('items', []))
        """
        return selector(self.state)


# =============================================================================
# 🎯 ARQUITECTURA: COMPONENT REGISTRY
# =============================================================================

class ComponentRegistry:
    """
    Registry centralizado de componentes/fragmentos para
    aplicaciones grandes y complejas.

    Permite:
    - Registrar fragmentos dinámicamente
    - Inyectar dependencias
    - Componer componentes
    - Resolver referencias por nombre
    """

    def __init__(self):
        self.components: Dict[str, Callable] = {}
        self.dependencies: Dict[str, list[str]] = {}

    def register(
        self,
        name: str,
        component: Callable,
        dependencies: list[str] = None
    ) -> None:
        """
        Registra un componente.

        Args:
            name: Identificador único
            component: Función del fragmento
            dependencies: Qué otros componentes necesita
        """
        self.components[name] = component
        self.dependencies[name] = dependencies or []

    def resolve_dependencies(self, component_name: str) -> Dict[str, Any]:
        """
        Resuelve e inyecta dependencias de un componente.

        Retorna dict con los componentes requeridos.
        """
        if component_name not in self.dependencies:
            return {}

        deps = {}
        for dep_name in self.dependencies[component_name]:
            if dep_name in self.components:
                deps[dep_name] = self.components[dep_name]

        return deps

    def render(self, component_name: str, **kwargs) -> None:
        """
        Renderiza un componente con sus dependencias inyectadas.

        Ejemplo:
            registry.render('dashboard', user_id=123)
        """
        if component_name not in self.components:
            st.error(f"Component not found: {component_name}")
            return

        component = self.components[component_name]
        deps = self.resolve_dependencies(component_name)

        # Inyecta dependencias + argumentos
        all_kwargs = {**deps, **kwargs}

        try:
            component(**all_kwargs)
        except Exception as e:
            st.error(f"Error rendering {component_name}: {e}")


# =============================================================================
# 🔀 ARQUITECTURA: COMPOSITION PATTERNS
# =============================================================================

class ComposableFragment:
    """
    Fragmento que puede componerse con otros fragmentos
    y mantener composición limpia.

    Uso:
        @ComposableFragment(depends_on=['fragment_a'])
        def my_fragment():
            st.write("I depend on fragment_a")
    """

    def __init__(self, depends_on: list[str] = None):
        self.depends_on = depends_on or []
        self.children: list[Callable] = []

    def __call__(self, func: Callable) -> Callable:
        """Actúa como decorador"""
        # Aquí va la lógica del decorador
        return func

    def add_child(self, child: Callable) -> "ComposableFragment":
        """Añade un fragmento hijo"""
        self.children.append(child)
        return self

    def render_children(self) -> None:
        """Renderiza todos los fragmentos hijo"""
        for child in self.children:
            if callable(child):
                child()


# =============================================================================
# 🚦 ARQUITECTURA: STATE MACHINE PATTERN
# =============================================================================

class FragmentStateMachine:
    """
    Implementa una máquina de estados para fragmentos complejos
    que tienen múltiples estados bien definidos.

    Uso:
        fsm = FragmentStateMachine()
        fsm.add_state('loading', on_enter=load_data)
        fsm.add_state('ready', on_enter=show_data)
        fsm.add_state('error', on_enter=show_error)
        fsm.transition('loading')
    """

    def __init__(self):
        self.states: Dict[str, Dict] = {}
        self.current_state: str = None
        self.previous_state: str = None
        self._in_session()

    def _in_session(self):
        """Persiste en session_state"""
        if '_fragment_fsm_state' not in st.session_state:
            st.session_state._fragment_fsm_state = {}

    def add_state(
        self,
        name: str,
        on_enter: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        render: Optional[Callable] = None,
    ) -> None:
        """
        Añade un estado a la máquina.

        Args:
            name: Nombre del estado
            on_enter: Se ejecuta al entrar
            on_exit: Se ejecuta al salir
            render: Se ejecuta para renderizar
        """
        self.states[name] = {
            'on_enter': on_enter,
            'on_exit': on_exit,
            'render': render,
        }

    def transition(self, new_state: str) -> bool:
        """
        Transiciona a un nuevo estado.

        Returns:
            True si la transición fue exitosa
        """
        if new_state not in self.states:
            return False

        # Ejecuta on_exit del estado anterior
        if self.current_state and self.states[self.current_state]['on_exit']:
            self.states[self.current_state]['on_exit']()

        self.previous_state = self.current_state
        self.current_state = new_state

        # Ejecuta on_enter del nuevo estado
        if self.states[new_state]['on_enter']:
            self.states[new_state]['on_enter']()

        return True

    def render(self) -> None:
        """Renderiza el estado actual"""
        if self.current_state and self.states[self.current_state]['render']:
            self.states[self.current_state]['render']()


# =============================================================================
# 🎪 ARQUITECTURA: CONTAINER/PRESENTER PATTERN
# =============================================================================

class Container:
    """
    Componente que gestiona lógica y estado.
    Delega renderizado a Presenters.

    Ejemplo:
        class UserContainer(Container):
            def __init__(self, user_id):
                self.user_id = user_id
                self.user = None

            def load_data(self):
                self.user = get_user(self.user_id)

            def render(self):
                self.load_data()
                UserPresenter(self.user)
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}

    def load_data(self) -> None:
        """Sobrescribir para cargar datos"""
        pass

    def render(self) -> None:
        """Sobrescribir para renderizar"""
        pass


class Presenter:
    """
    Componente que SOLO renderiza datos.
    No contiene lógica ni estado.

    Ejemplo:
        class UserPresenter(Presenter):
            def __init__(self, user):
                self.user = user

            def render(self):
                st.write(f"User: {self.user['name']}")
    """

    def __init__(self, **props):
        self.props = props

    def render(self) -> None:
        """Sobrescribir para renderizar"""
        pass


# =============================================================================
# 📋 ARQUITECTURA: FORM STATE MANAGEMENT
# =============================================================================

@dataclass
class FormState:
    """Estado de un formulario reactivo"""
    values: Dict[str, Any]
    errors: Dict[str, str]
    touched: set
    is_submitting: bool = False
    is_valid: bool = False


class ReactiveForm:
    """
    Formulario reactivo que valida mientras escribes.

    Uso:
        form = ReactiveForm(initial_values={'name': '', 'email': ''})
        form.add_validator('email', validate_email)
        form.add_field('name', 'text')
        form.add_field('email', 'email')

        if form.render():  # Returns True if valid and submitted
            process_form(form.values)
    """

    def __init__(self, initial_values: Dict[str, Any]):
        self.initial_values = initial_values
        self.validators: Dict[str, Callable] = {}
        self.fields: Dict[str, str] = {}
        self._init_state()

    def _init_state(self):
        if '_form_state' not in st.session_state:
            st.session_state._form_state = {
                'values': self.initial_values.copy(),
                'errors': {},
                'touched': set(),
            }

    def add_field(self, name: str, field_type: str = 'text') -> None:
        """Registra un campo"""
        self.fields[name] = field_type

    def add_validator(
        self,
        field: str,
        validator: Callable[[Any], Optional[str]]
    ) -> None:
        """
        Registra un validador.
        Debe retornar None si es válido, o mensaje de error.
        """
        self.validators[field] = validator

    def render(self) -> bool:
        """
        Renderiza el formulario.
        Retorna True si se envió y es válido.
        """
        state = st.session_state._form_state

        # Renderiza campos
        for field_name, field_type in self.fields.items():
            col1, col2 = st.columns([3, 1])

            with col1:
                if field_type == 'text':
                    state['values'][field_name] = st.text_input(
                        field_name,
                        value=state['values'].get(field_name, ''),
                    )
                elif field_type == 'email':
                    state['values'][field_name] = st.text_input(
                        field_name,
                        value=state['values'].get(field_name, ''),
                        type='password' if 'password' in field_name else 'default',
                    )
                elif field_type == 'number':
                    state['values'][field_name] = st.number_input(
                        field_name,
                        value=state['values'].get(field_name, 0),
                    )

            # Validación y error
            with col2:
                if field_name in self.validators:
                    error = self.validators[field_name](
                        state['values'].get(field_name)
                    )
                    if error:
                        st.error(error)
                        state['errors'][field_name] = error
                    else:
                        state['errors'].pop(field_name, None)

        # Botón de envío
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.button("Submit")
        with col2:
            if st.button("Reset"):
                st.session_state._form_state = {
                    'values': self.initial_values.copy(),
                    'errors': {},
                    'touched': set(),
                }
                st.rerun()

        if submitted and not state['errors']:
            return True

        return False

    @property
    def values(self):
        return st.session_state._form_state['values']


# =============================================================================
# 🔌 ARQUITECTURA: MIDDLEWARE PATTERN
# =============================================================================

class FragmentMiddleware:
    """
    Middleware que intercepta y modifica fragmentos antes/después
    de renderizar.

    Útil para:
    - Logging
    - Profiling
    - Error handling
    - Loading states
    """

    def before_render(self, fragment_name: str) -> None:
        """Se ejecuta antes de renderizar"""
        pass

    def after_render(self, fragment_name: str) -> None:
        """Se ejecuta después de renderizar"""
        pass

    def on_error(self, fragment_name: str, error: Exception) -> None:
        """Se ejecuta si hay error"""
        pass


class LoggingMiddleware(FragmentMiddleware):
    def before_render(self, fragment_name: str) -> None:
        st.session_state._logs = (
            st.session_state.get('_logs', []) +
            [f"→ Rendering {fragment_name}"]
        )

    def after_render(self, fragment_name: str) -> None:
        st.session_state._logs = (
            st.session_state.get('_logs', []) +
            [f"✓ Rendered {fragment_name}"]
        )


class LoadingMiddleware(FragmentMiddleware):
    def before_render(self, fragment_name: str) -> None:
        with st.spinner(f"Loading {fragment_name}..."):
            pass

    def after_render(self, fragment_name: str) -> None:
        st.success(f"{fragment_name} loaded!")


# =============================================================================
# 📝 EJEMPLO COMPLETO: TODO APP CON PATRONES AVANZADOS
# =============================================================================

def example_todo_app():
    """
    Ejemplo de aplicación TODO que usa:
    - ReactiveStore para estado global
    - FormState para manejo de formularios
    - StateMachine para UI states
    - Presenters para renderizado limpio
    """
    # Inicializa store
    if '_todo_store' not in st.session_state:
        store = ReactiveStore()

        # Define acciones
        store.define_action(
            'ADD_TODO',
            lambda state, todo: {
                **state,
                'todos': state.get('todos', []) + [todo]
            }
        )

        store.define_action(
            'REMOVE_TODO',
            lambda state, idx: {
                **state,
                'todos': [
                    t for i, t in enumerate(state.get('todos', []))
                    if i != idx
                ]
            }
        )

        st.session_state._todo_store = store

    store = st.session_state._todo_store

    st.title("TODO App with Advanced Patterns")

    # Formulario para agregar TODOs
    with st.form("add_todo_form"):
        todo_text = st.text_input("What to do?")
        submitted = st.form_submit_button("Add")

        if submitted and todo_text:
            store.dispatch(Action('ADD_TODO', {'text': todo_text, 'done': False}))
            st.rerun()

    # Muestra TODOs
    todos = store.get('todos', [])
    for i, todo in enumerate(todos):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(todo['text'])
        with col2:
            st.checkbox("Done", value=todo.get('done', False))
        with col3:
            if st.button("Remove", key=f"remove_{i}"):
                store.dispatch(Action('REMOVE_TODO', i))
                st.rerun()


# Exporta para uso en otras aplicaciones
__all__ = [
    'ReactiveStore',
    'Action',
    'ComponentRegistry',
    'ComposableFragment',
    'FragmentStateMachine',
    'Container',
    'Presenter',
    'FormState',
    'ReactiveForm',
    'FragmentMiddleware',
    'LoggingMiddleware',
    'LoadingMiddleware',
    'example_todo_app',
]

