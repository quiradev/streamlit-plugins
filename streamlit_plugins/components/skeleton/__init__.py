import contextlib
import sys
import uuid
from typing import Literal, Any, Iterator

import streamlit as st
from streamlit.components.v2 import component as create_component
from streamlit.delta_generator import DeltaGenerator
from streamlit.elements.lib.layout_utils import Width
from streamlit.proto.Skeleton_pb2 import Skeleton as SkeletonProto

from .template_builder import StreamlitSkeletonBuilder

SKELETON_BASE_CSS = """
<style>
:has(> .st-key-SKELETON_KEY) {
    flex-direction: row;
}

.stSkeleton {
    background: var(--st-gray-background-color);
    border-radius: 0.5rem;
    animation-duration: 750ms;
    animation-name: skeleton;
    animation-timing-function: ease-in;
    animation-direction: normal;
    animation-iteration-count: infinite;

}
@keyframes skeleton {
    0%, 100% {
        opacity: 0.5;
    }
    50% {
        opacity: 1;
    }
}
</style>
"""

SKELETON_LIST = """
<div style="display: flex; align-items: center; gap: 16px; padding: 12px 0;">
  <div class="stSkeleton" style="width: 50px; height: 50px; border-radius: 50%; flex-shrink: 0;"></div>
  <div style="display: flex; flex-direction: column; gap: 8px; flex-grow: 1;">
    <div class="stSkeleton" style="width: 40%; height: 18px; border-radius: 4px;"></div>
    <div class="stSkeleton" style="width: 70%; height: 14px; border-radius: 4px;"></div>
  </div>
  <div class="stSkeleton" style="width: 24px; height: 24px; border-radius: 4px;"></div>
</div>
"""
SKELETON_PAGE = """
<div style="max-width: 800px; margin: 0 auto; padding: 24px;">

  <!-- Cabecera: Título y subtítulo -->
  <div style="margin-bottom: 32px;">
    <div class="stSkeleton" style="width: 60%; height: 40px; border-radius: 8px; margin-bottom: 12px;"></div>
    <div class="stSkeleton" style="width: 30%; height: 16px; border-radius: 4px;"></div>
  </div>

  <!-- Contenido dividido en 2 columnas -->
  <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 32px;">

    <!-- Columna Principal (Texto largo) -->
    <div style="display: flex; flex-direction: column; gap: 12px;">
      <div class="stSkeleton" style="width: 100%; height: 16px; border-radius: 4px;"></div>
      <div class="stSkeleton" style="width: 100%; height: 16px; border-radius: 4px;"></div>
      <div class="stSkeleton" style="width: 90%; height: 16px; border-radius: 4px;"></div>
      <div class="stSkeleton" style="width: 95%; height: 16px; border-radius: 4px;"></div>
      <div class="stSkeleton" style="width: 50%; height: 16px; border-radius: 4px;"></div>
    </div>

    <!-- Columna Secundaria (Widget o info extra) -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div class="stSkeleton" style="width: 100%; height: 150px; border-radius: 8px;"></div>
      <div class="stSkeleton" style="width: 100%; height: 60px; border-radius: 8px;"></div>
    </div>

  </div>
</div>
"""

_SKELETON_COMPONENT = create_component(
    "custom_skeleton_v2",
    html="""
<div id="skeleton-root"></div>
""",
    js="""
export default function({ parentElement, data }) {
    const root = parentElement.querySelector("#skeleton-root");
    if (!root) {
        return;
    }
    root.innerHTML = data?.html || "";
}
""",
    css="",
    isolate_styles=False,
)


def _render_skeleton_component(skeleton_placeholder: DeltaGenerator, html_content: str, key: str):
    with skeleton_placeholder:
        _SKELETON_COMPONENT(
            data={"html": f"{SKELETON_BASE_CSS.replace('SKELETON_KEY', key)}{html_content}"},
            key=key,
        )
    return skeleton_placeholder


_BASE_STYLE_TEMPLATES: dict[str, str] = {
    "list": SKELETON_LIST,
    "page": SKELETON_PAGE,
}


def _resolve_height(height: int | str | None, width: Width | int) -> int:
    if isinstance(height, int) and height > 0:
        return height

    if isinstance(height, str) and height.isdigit():
        parsed_height = int(height)
        if parsed_height > 0:
            return parsed_height

    if isinstance(width, int) and width > 0:
        return width

    if isinstance(width, str) and width.isdigit():
        parsed_width = int(width)
        if parsed_width > 0:
            return parsed_width

    return 100


def _resolve_width_css(width: Width | int) -> str | None:
    if isinstance(width, int) and width > 0:
        return f"{width}px"

    if isinstance(width, str):
        if width.isdigit() and int(width) > 0:
            return f"{int(width)}px"
        if width == "stretch":
            return "100%"
        if width == "content":
            return "fit-content"

    return None


@contextlib.contextmanager
def st_hidden_container(key: str | None = None) -> Iterator[DeltaGenerator]:
    """Crea un contenedor oculto y cede el placeholder del CSS para que el caller lo controle."""
    key = key or f"skeleton-hide-content-{uuid.uuid4().hex}"
    with st.container(key=key):
        hide_placeholder = st.markdown(
            f"<style>:has(>.st-key-{key}) {{visibility: hidden; opacity: 0; width: 100%; margin-left: -100%;}}</style>",
            unsafe_allow_html=True,
        )
        yield hide_placeholder
        # El caller ya habrá vaciado hide_placeholder; aquí no hacemos nada


class SkeletonResult:
    """
    Objeto retornado por st_skeleton.

    - Modo contexto (base_style / template):
        Muestra el skeleton mientras se ejecuta el bloque `with`,
        luego lo borra y muestra el contenido real.

    - Modo simple (width / height):
        Retorna un proxy del DeltaGenerator nativo de Streamlit
        para poder llamar skeleton.image(...) etc.
    """

    def __init__(
            self,
            *,
            base_style: Literal["list", "page"] | None,
            template: str | None,
            width: Width | int,
            height: int | str | None,
            key_id: str,
    ) -> None:
        self._base_style = base_style
        self._template = template
        self._width = width
        self._height = height
        self._key_id = key_id
        self._hidden_key_id = f"hidden-{self._key_id}"
        self._is_context_mode = base_style is not None or template is not None
        self._skeleton_placeholder: DeltaGenerator | None = None
        self._hidden_ctx: Any = None
        self._hide_placeholder: DeltaGenerator | None = None
        self._dg: DeltaGenerator | None = None

        if not self._is_context_mode:
            self._dg = self._render_simple()

    def _render_simple(self) -> DeltaGenerator:
        resolved_height = _resolve_height(self._height, self._width)
        width_css = _resolve_width_css(self._width)
        with st.container(key=self._key_id):
            if width_css:
                st.markdown(
                    f"<style>.st-key-{self._key_id} .stSkeleton {{width: {width_css};}}</style>",
                    unsafe_allow_html=True,
                )
            return st._main._enqueue("skeleton", SkeletonProto(style=0, height=resolved_height))

    # ── Context manager protocol ──────────────────────────────────────────────

    def __enter__(self) -> None:
        html = (
            _BASE_STYLE_TEMPLATES[self._base_style]
            if self._base_style
            else self._template
        )
        skeleton_ph = st.empty()
        self._skeleton_placeholder = skeleton_ph
        html_str: str = html or ""
        _render_skeleton_component(skeleton_ph, html_str, self._key_id)
        self._hidden_ctx = st_hidden_container(key=self._hidden_key_id)
        # __enter__ del contextmanager pausa en yield y devuelve hide_placeholder
        self._hide_placeholder = self._hidden_ctx.__enter__()
        return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        # 1. Quitar visibility/opacity pero mantener width/margin-left
        #    para que el contenido real no "salte" mientras el skeleton desaparece.
        if self._hide_placeholder is not None:
            _selector = f":has(> div >.st-key-{self._hidden_key_id}):not(:has(>.stElementContainer > .stEmpty)) > :has(> .st-key-{self._hidden_key_id})"
            self._hide_placeholder.markdown(
                f"<style>{_selector} {{width: 100%; margin-left: -100%;}} :has(> .stElem</style>",
                unsafe_allow_html=True,
            )

        # 2. Eliminar el skeleton
        if self._skeleton_placeholder is not None:
            self._skeleton_placeholder.empty()

        # 3. Eliminar también el CSS de posición → el contenido real queda visible
        if self._hide_placeholder is not None:
            self._hide_placeholder.empty()

        # 4. Cerrar el contextmanager de st_hidden_container (sale del st.container)
        if self._hidden_ctx is not None:
            self._hidden_ctx.__exit__(exc_type, exc_val, exc_tb)

        return False

    # ── DeltaGenerator proxy (modo simple) ───────────────────��───────────────

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        dg = object.__getattribute__(self, "_dg")
        if dg is not None:
            return getattr(dg, name)
        raise AttributeError(
            f"'SkeletonResult' no tiene '{name}'. "
            "Los atributos de DeltaGenerator solo están disponibles en modo simple (width/height)."
        )


def st_skeleton(
        *,
        base_style: Literal["list", "page"] | None = None,
        template: str | None = None,
        builder: StreamlitSkeletonBuilder | None = None,
        width: Width | int = "stretch",
        height: int | str | None = None,
        key: str | None = None,
) -> SkeletonResult:
    if builder is not None:
        if template is not None:
            raise ValueError("No puedes usar `template` y `builder` al mismo tiempo.")
        if base_style is not None:
            raise ValueError("No puedes usar `base_style` y `builder` al mismo tiempo.")
        template = builder.build()

    key_id: str = key or f"skeleton-{uuid.uuid4().hex}"
    return SkeletonResult(
        base_style=base_style,
        template=template,
        width=width,
        height=height,
        key_id=key_id,
    )


st._main.skeleton = st_skeleton
st.skeleton = st_skeleton
sys.modules["streamlit"].skeleton = st_skeleton
sys.modules["streamlit"] = st

__all__ = ["StreamlitSkeletonBuilder", "st_skeleton"]
