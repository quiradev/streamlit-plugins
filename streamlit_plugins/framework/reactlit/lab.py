"""
Reactive Fragments Runtime for Streamlit >= 1.53
================================================

Este fichero implementa un mini-runtime para:
- Disparar reruns de fragments desde backend
- Encadenar fragments por dependencias lógicas
- Reaccionar a cambios de widgets sin tocar el layout
- Usar el MISMO mecanismo que los timers de Streamlit

NO usa API pública. Es intencional.
"""
import inspect
import typing

import streamlit as st
from streamlit.commands.execution_control import _new_fragment_id_queue

# =========================
# 🔧 LOW-LEVEL IMPORTS
# =========================

from streamlit.runtime.scriptrunner import (
    get_script_run_ctx,
    RerunData,
)

# =========================
# 🧠 FRAGMENT TRIGGER CORE
# =========================

def trigger_fragment_by_name(fragment_func_name: str) -> bool:
    """
    Dispara un rerun de un fragment concreto SIN llamarlo,
    SIN modificar layout y SIN widget interaction.

    Devuelve True si se pudo disparar, False si no existe.
    """
    ctx = get_script_run_ctx()
    if ctx is None:
        return False

    fragment_storage = ctx.fragment_storage

    for fragment_id, fragment in fragment_storage.fragments.items():
        if fragment.func.__name__ == fragment_func_name:
            rerun_data = RerunData(
                fragment_id=fragment_id,
                widget_states=None,  # backend-driven (igual que timers)
                page_script_hash=ctx.page_script_hash,
            )
            ctx.session.request_rerun(rerun_data)
            return True

    return False

def get_declared_defaults(func):
    # Si viene decorada con @wraps, recupera la original
    orig = getattr(func, "__wrapped__", func)

    sig = inspect.signature(orig)
    params = sig.parameters

    positional_defaults = {}
    kwonly_defaults = {}

    for name, p in params.items():
        if p.default is not inspect.Parameter.empty:
            if p.kind is inspect.Parameter.KEYWORD_ONLY:
                kwonly_defaults[name] = p.default
            else:
                positional_defaults[name] = p.default

    return {
        "original_func": orig,
        "signature": sig,
        "positional_or_keyword_defaults": positional_defaults,
        "keyword_only_defaults": kwonly_defaults,
    }


def get_param_types(func):
    orig = getattr(func, "__wrapped__", func)
    sig = inspect.signature(orig)

    # Resuelve anotaciones reales (incluye forward refs si puede)
    try:
        resolved_hints = typing.get_type_hints(orig)
    except Exception:
        resolved_hints = {}

    params_info = {}
    for name, p in sig.parameters.items():
        has_annotation = p.annotation is not inspect.Parameter.empty

        # Prioriza anotación resuelta; fallback a la cruda de inspect
        ann = resolved_hints.get(
            name,
            None if not has_annotation else p.annotation
        )

        params_info[name] = {
            "has_type": has_annotation,
            "type": ann,  # None si no hay anotación
            "kind": p.kind,  # opcional, por si te sirve
            "has_default": p.default is not inspect.Parameter.empty,
            "default": None if p.default is inspect.Parameter.empty else p.default,
        }

    return_annotation = sig.return_annotation
    has_return_type = return_annotation is not inspect.Signature.empty
    return_type = resolved_hints.get(
        "return",
        None if not has_return_type else return_annotation
    )

    return {
        "original_func": orig,
        "signature": sig,
        "params": params_info,
        "return": {
            "has_type": has_return_type,
            "type": return_type,
        },
    }
# =========================
# 🔍 WIDGET CHANGE DETECTOR
# =========================
def run_fragments(fragment_ids: list[str]):
    """
    ctx.current_fragment_id: Te da el identificador actual del fragmento
    ctx.current_fragment_delta_path: Te devuelve el delta path del fragmento donde se ejecute
    ctx.fragment_ids_this_run: Es el path de ejecuciones que hacen trigger, es decir el punto de entrada
    Ademas el fragment id se genera con el siguiente codigo
    ```python
    fragment_id = calc_md5(
        f"{non_optional_func.__module__}.{get_object_name(non_optional_func)}{dg_stack_snapshot[-1]._get_delta_path_str()}{additional_hash_info}"
    )
    ```
    El tema es que se actualiza el wrapper con la ultima llamada a ese wrapper del fragmento, lo que significa
    que si esta parametrizado ese fragmento se queda una foto de los parametros de entrada, por lo que si hay reruns
    estos reruns seguiran haciendose siempre con esos parametros de entrada, la unica forma de modificar esos parameotrs
    seria dentro del propio fragmento antes de hacer un rerun fragment modificar el fragment storage, haciendo un wrapper
    del fragmento

    Por lo que para modificar las variables o atributos enclaustrados dentro del wrapper se puede recurrir a las freevars interanas del wrapper

    ```python
    wrapped_f = ctx.fragment_storage._fragments[fragment_id]
    wrapped_f_vars = wrapped_f.__code__.co_freevars
    args = wrapped_f.__closure__[wrapped_f_vars.index("args")].cell_contents
    kwargs = wrapped_f.__closure__[wrapped_f_vars.index("kwargs")].cell_contents

    new_args = tuple()
    new_kwargs = {}

    wrapped_f.__closure__[wrapped_f_vars.index("args")].cell_contents = new_args
    wrapped_f.__closure__[wrapped_f_vars.index("kwargs")].cell_contents = new_kwargs

    ```

    Despues si se quiere settear los valores por defecto de la funcion se recuperan de la funcion original
    Directamente, la funcion X, importandola o accediendo, y si es algo abstracto se puede recuperar dinamicamente

    ```python
    original_func = wrapped_f.__closure__[wrapped_f_vars.index("non_optional_func")].cell_contents
    info_original_func = get_declared_defaults(original_func)
    ```
    :param fragment_ids:
    :return:
    """
    ctx = get_script_run_ctx()
    if ctx and ctx.script_requests:
        query_string = ctx.query_string
        page_script_hash = ctx.page_script_hash
        cached_message_hashes = ctx.cached_message_hashes

        fragment_queue = _new_fragment_id_queue(ctx, "fragment")
        ctx.script_requests.request_rerun(
            RerunData(
                query_string=query_string,
                page_script_hash=page_script_hash,
                fragment_id_queue=fragment_queue,
                is_fragment_scoped_rerun=True,
                cached_message_hashes=cached_message_hashes,
                context_info=ctx.context_info,
            )
        )
        # Force a yield point so the runner can do the rerun
        st.empty()

def get_changed_widget_keys():
    """
    Devuelve los widget_ids que participaron en el rerun actual.
    Si el rerun no viene del frontend → lista vacía.
    """
    ctx = get_script_run_ctx()
    if ctx is None or ctx.widget_states is None:
        return []
    fragment_storage = ctx.fragment_storage
    if ctx is None or fragment_storage is None:
        return []

    fragment_storage._fragments
    st.rerun
    return list(ctx.widget_states.keys())


# =========================
# 🧩 REACTIVE RULE ENGINE
# =========================

def reactive_rules():
    """
    Aquí defines TODA la lógica reactiva de tu framework.
    No toca layout. No llama fragments.
    SOLO decide qué fragmentos deben reejecutarse.


    """
    # changed_widgets = get_changed_widget_keys()
    #
    # # Ejemplo: si cambia cualquier widget que termine en 'filter'
    # for wid in changed_widgets:
    #     if wid.endswith("filter"):
    #         trigger_fragment_by_name("fragment_b")
    #
    # # Ejemplo de dependencia por estado
    # if st.session_state.get("force_c"):
    #     trigger_fragment_by_name("fragment_c")
    #     st.session_state.force_c = False


# =========================
# 🧱 FRAGMENTS DE EJEMPLO
# =========================

@st.fragment
def fragment_a():
    """
    Fragmento A:
    - Tiene widgets
    - Genera estado
    """
    ctx = get_script_run_ctx()
    st.subheader(f"Fragment A ({ctx.current_fragment_id})")

    st.selectbox(
        "Filtro",
        ["Uno", "Dos", "Tres"],
        key="a_filter",
    )

    if st.button("Forzar C"):
        fragment_b()
        st.session_state.force_c = True

    st.write("Estado actual:", st.session_state.get("a_filter"))


@st.fragment()
def fragment_b(rerun=True):
    """
    Fragmento B:
    - Depende de A
    - Se rerunea cuando cambia el filtro
    """
    ctx = get_script_run_ctx()
    st.subheader(f"Fragment B ({ctx.current_fragment_id})")
    st.write("Renderizando B porque cambió el filtro")
    st.write("Filtro actual:", st.session_state.get("a_filter"))
    fragment_c(False, a=2)
    fragment_c(rerun=rerun)




@st.fragment()
def fragment_c(rerun: bool, a = 1):
    """
    Fragmento C:
    - Se dispara solo por backend
    """
    ctx = get_script_run_ctx()
    st.subheader(f"Fragment C {a} ({ctx.current_fragment_id})")
    st.success("C ejecutado por trigger backend")
    if rerun:
        st.rerun(scope="fragment")


def main():
    # =========================
    # 🧭 LAYOUT (FIJO)
    # =========================

    st.title("Reactive Fragments Runtime Demo")


    fragment_a()

    # with col2:
    #     fragment_b()
    #
    # with col3:
    #     fragment_c()

    # =========================
    # 🚦 REACTIVE ENGINE ENTRY
    # =========================

    # IMPORTANTE:
    # Esto se ejecuta en CADA rerun,
    # pero SOLO dispara fragments si hay señales reales.
    reactive_rules()

if __name__ == '__main__':
    main()
