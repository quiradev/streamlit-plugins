# Guía de Arquitectura - Reactlit Framework

## 📐 Arquitectura General

El framework reactivo de Streamlit se divide en tres capas:

```
┌─────────────────────────────────────┐
│     REACTIVE FRAGMENT DECORATOR      │  @reactive_fragment()
│     (API Pública)                   │
├─────────────────────────────────────┤
│     DEPENDENCY MANAGEMENT           │  Grafo, Ciclos, Cadenas
│     (Lógica Central)                │
├─────────────────────────────────────┤
│     STATE MANAGEMENT                │  Session State, Storage
│     (Persistencia)                  │
├─────────────────────────────────────┤
│     STREAMLIT RUNTIME               │  Fragment API, Reruns
│     (Integración)                   │
└─────────────────────────────────────┘
```

## 🏛️ Componentes Principales

### 1. Core Data Structures (`reactive.py`)

```python
FragmentMetadata:
  - name: str                    # Identificador único
  - func: Callable              # Función original
  - dependencies: Set[str]      # Qué observa
  - dependents: Set[str]        # Quién lo usa
  - param_watchers: dict        # Últimos valores
  - is_dirty: bool              # Necesita rerun

DependencyGraph:
  - fragments: dict             # Todos los fragmentos
  - rerun_queue: list          # Cola de ejecución
  - get_dependents_chain()     # Calcula cadena transitiva
  - has_cycle()                # Detecta ciclos infinitos
```

### 2. Registro Global

```python
_GLOBAL_REGISTRY: dict[str, FragmentMetadata]
  └─ Almacena metadatos de todos los fragmentos
  └─ Se actualiza cuando se aplica @reactive_fragment()

_GLOBAL_GRAPH: DependencyGraph
  └─ Mantiene el grafo de dependencias
  └─ Detecta ciclos y calcula cadenas

_FRAGMENT_ID_TO_NAME: dict[str, str]
  └─ Mapea ID interno de Streamlit a nombre de fragmento
```

### 3. Session State

```python
st.session_state._reactive_graph_state:
  - rerun_queue: list[str]      # Fragmentos a ejecutar
  - executing: Set[str]         # En ejecución ahora
  - last_params: dict           # Últimos parámetros
  - fragment_ids: dict          # Mapeos de IDs

st.session_state._fragment_state_{name}:
  - params: dict                # Parámetros actuales
  - is_dirty: bool              # Necesita rerun
  - last_rendered_params: dict  # Último renderizado
```

## 🔄 Flujo de Ejecución

### Fase 1: Renderizado Inicial

```
┌─────────────────────────┐
│  Primera ejecución del  │
│  script Streamlit       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Decorador              │
│  @reactive_fragment()   │
└────────────┬────────────┘
             │
             ├─ Registra en _GLOBAL_REGISTRY
             ├─ Añade al DependencyGraph
             └─ Inicializa state en session
             │
             ▼
┌─────────────────────────┐
│  wrapper() ejecuta      │
│  - Detecta cambios      │
│  - Ejecuta función      │
│  - Marca dependientes   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Renderizado en UI      │
└─────────────────────────┘
```

### Fase 2: Detección de Cambios

```
Widget cambia en Fragment A
         │
         ▼
_detect_param_changes()
         │
         ├─ Compara con last_rendered_params
         └─ Si hay cambios:
             │
             ▼
         _mark_dependents_dirty()
             │
             └─ Todos los que dependen de A
                 │
                 ▼
             Marcar como dirty
                 │
                 ▼
             st.rerun(scope="fragment")
```

### Fase 3: Procesamiento de Cola

```
Hay items en rerun_queue
         │
         ▼
_process_rerun_queue()
         │
         ├─ Pop del primer fragmento
         │
         ├─ _trigger_fragment_rerun()
         │   │
         │   └─ ctx.session.request_rerun()
         │
         ├─ Streamlit rerunnea ese fragmento
         │
         └─ Al terminar, loop del siguiente
```

## 🧮 Detección de Cambios

### Hash-based Comparison

```python
def _compute_param_hash(params: dict) -> str:
    """
    Convierte dict de parámetros a string
    Calcula MD5 hash
    Usa para comparación rápida
    """
```

### Value Comparison

```python
for key, new_value in current_params.items():
    old_value = last_params.get(key)
    if old_value != new_value:
        changed_params.add(key)
```

## 🕸️ Grafo de Dependencias

### Estructura Interna

```
Fragmento A
├─ dependencies: {key1, B}    # Observa key1 y fragmento B
├─ dependents: {C}            # Fragmento C lo usa
└─ param_watchers: {}         # Últimos valores observados

Fragmento B
├─ dependencies: {}
├─ dependents: {A, D}
└─ param_watchers: {}

Fragmento C
├─ dependencies: {A}
├─ dependents: {E}
└─ param_watchers: {}
```

### Cálculo de Cadena Transitiva

```
get_dependents_chain('A')
    │
    ├─ A → {C}           Directo
    │
    ├─ C → {E}           Transitivo
    │
    └─ Resultado: {C, E}
```

### Detección de Ciclos (DFS)

```
has_cycle('A'):
    │
    ├─ A → B
    │      │
    │      └─ B → C
    │             │
    │             └─ C → A  ✓ CICLO ENCONTRADO
    │
    └─ return True
```

## 🔌 Integración con Streamlit

### Fragment API Usage

```python
@st.fragment(...)
def wrapper(*args, **kwargs):
    # Nuestro código
    ctx = get_script_run_ctx()
    # Accedemos a:
    # - ctx.fragment_storage    # Todos los fragmentos
    # - ctx.session             # Para request_rerun
    # - ctx.current_fragment_id # ID actual
    # - ctx.widget_states       # Widgets modificados
```

### Rerun Request

```python
rerun_data = RerunData(
    fragment_id=fragment_id,        # Qué fragmento
    widget_states=None,             # Backend-driven (sin widget)
    page_script_hash=ctx.page_script_hash
)
ctx.session.request_rerun(rerun_data)
```

## 🏗️ Patrones de Composición

### 1. Linear Cascade

```
Control → Process → Analyze → Visualize
```

- A cambia → Marca B dirty
- B se ejecuta → Marca C dirty
- C se ejecuta → Marca D dirty
- D se ejecuta

### 2. Tree Structure

```
       Root
      /    \
    Left  Right
   / \      |
  A   B     C
```

- Root cambia → Marca Left y Right dirty
- Left cambia → Marca A y B dirty
- Right cambia → Marca C dirty

### 3. Diamond (con cuidado)

```
     A
    / \
   B   C
    \ /
     D
```

- A cambia → Marca B y C dirty
- B y C → Marcan D dirty (puede ejecutarse 2x)
- **Solución**: Usar `prevent_cycles=True`

## 🛡️ Prevención de Ciclos

```python
if prevent_cycles and has_dependency_cycle(fragment_name):
    # No rerunea
    return
```

## 📊 Performance Considerations

### Overhead por Fragmento

- Detección de cambios: O(n) donde n = parámetros
- Búsqueda de dependientes: O(m) donde m = dependencias
- Grafo total: O(f*d) donde f = fragmentos, d = dependencias promedio

### Optimizaciones

1. **Lazy Evaluation**: Solo procesa si hay cambios
2. **Caching de cadenas**: Calcula cadena una sola vez
3. **Visited Set**: En ciclos, evita revisitar

## 🔧 Extensiones Posibles

### 1. Async Fragments

```python
async def async_fragment():
    await asyncio.sleep(1)
    st.write("Done")
```

### 2. Memoization

```python
@reactive_fragment(memo=True)
def expensive_calculation():
    pass
```

### 3. Custom Events

```python
fragment.emit('data_changed', {'value': 42})
fragment.on('data_changed', callback)
```

### 4. Fragments Plugin System

```python
ReactiveStore  # Redux-like
FormManager    # Forms complejos
StateFactory   # Factory de estados
```

## 🐛 Debugging interno

### Logs Framework

```python
st.session_state._reactive_framework_log
# [
#   "[QUEUE] fragment_a reason",
#   "[CHANGE] fragment_b: {'param1'}",
#   "[CYCLE] Detected in fragment_c",
# ]
```

### Introspection

```python
get_all_fragments()           # Todos registrados
get_fragment_metadata(name)   # Metadatos específicos
get_fragment_state(name)      # Estado actual
has_dependency_cycle(name)    # ¿Hay ciclo?
```

## 📚 Comparación con Alternativas

### vs. Manual st.rerun()

```
❌ Manual:
if st.session_state.changed:
    st.rerun()
    st.rerun()  # Hay que llamar explícitamente

✅ Reactlit:
# Automático, detecta todo
```

### vs. Callbacks de widgets

```
❌ Callbacks:
st.slider(..., on_change=my_callback)
# Limitado, solo widgets

✅ Reactlit:
# Cualquier cambio, fragmentos enteros
```

### vs. Custom hooks (React-like)

```
❌ React hooks:
# No existen en Streamlit

✅ Reactlit:
# Similar a React Effects/Deps
```

## 🎯 Use Cases

### ✅ Ideal para:

- Dashboards interactivos con múltiples paneles
- Workflows multi-paso dependientes
- Análisis exploratorio con cascadas de cálculos
- Sistemas de configuración complejos
- Procesamiento de datos con feedback

### ❌ No ideal para:

- Aplicaciones con HTML/CSS muy complejas
- Games o aplicaciones con estados muy finos
- Lógica estrictamente imperativa

---

**Última actualización**: 2026-04-11
**Versión Framework**: 0.1.0

