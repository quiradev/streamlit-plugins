# Reactlit - Reactive Fragment Framework for Streamlit

> Framework avanzado para crear componentes reactivos (fragmentos) en Streamlit con detección automática de cambios, gestión de dependencias y cascadas de reruns.

## 🎯 Características Principales

- ✅ **Fragmentos Reactivos**: Componentes que se actualizan automáticamente
- ✅ **Grafo de Dependencias**: Mapeo automático de relaciones entre fragmentos
- ✅ **Detección de Cambios**: Observa parámetros y estado compartido
- ✅ **Cascadas de Reruns**: Ejecuta cadenas de actualizaciones automáticamente
- ✅ **Prevención de Ciclos**: Detecta y evita loops infinitos
- ✅ **State Compartido**: Integración con `session_state` de Streamlit
- ✅ **Patrones Avanzados**: Redux/Flux, Forms, State Machines, DI

## 🚀 Inicio Rápido

### Instalación

```bash
pip install streamlit-plugins
```

### Ejemplo Básico

```python
import streamlit as st
from streamlit_plugins.framework.reactlit import reactive_fragment

st.set_page_config(page_title="My App", layout="wide")

# Define un fragmento raíz que no depende de nada
@reactive_fragment(watch_params=True)
def controls():
    """Panel de controles - Input"""
    value = st.slider("Selecciona un valor:", 0, 100)
    st.session_state.selected_value = value

# Define un fragmento que depende de controls
@reactive_fragment(
    dependencies=['selected_value'],
    watch_params=True
)
def display_result():
    """Panel de resultados - Output"""
    value = st.session_state.get('selected_value', 0)
    result = value ** 2
    st.metric("Valor al cuadrado", result)

# Ejecuta la aplicación
controls()
display_result()
```

**Resultado**: Cuando cambies el slider, `display_result()` se rerunnea automáticamente.

## 📚 Conceptos Clave

### 1. Fragmentos Reactivos

Un fragmento reactivo es una función decorada con `@reactive_fragment`:

```python
@reactive_fragment(
    dependencies=['input_key'],  # Observa cambios en session_state
    watch_params=True             # Detecta cambios en parámetros
)
def my_component(param1, param2=None):
    st.write(f"Parámetro 1: {param1}")
    # Se renderiza cuando:
    # - input_key cambia
    # - param1 o param2 cambian como parámetros
```

### 2. Dependencias

Las dependencias pueden ser:

- **Session state keys**: Valores en `st.session_state` que el fragmento observa
- **Otros fragmentos**: Nombres de fragmentos de los cuales depende

```python
@reactive_fragment(
    dependencies=['user_id', 'filter_options', 'data_loader']
)
def render_panel():
    user = st.session_state.user_id
    filters = st.session_state.filter_options
    # Se actualiza si user_id, filter_options o data_loader cambian
```

### 3. Cambios de Parámetros

Con `watch_params=True`, el framework detecta cambios en los parámetros:

```python
@reactive_fragment(watch_params=True)
def processor(data, threshold=0.5):
    # Si 'data' o 'threshold' cambian → se marca dependientes como dirty
    st.write(f"Procesando {len(data)} items")
```

### 4. Grafo de Dependencias

El framework mantiene un grafo que mapea todas las relaciones:

```
Controles → Carga de Datos → Análisis → Visualizaciones
   ↓              ↓              ↓           ↓
Input      Session State   Computación   Charts
```

Cuando cambia algo:
1. Se detecta el cambio
2. Se marcan todos los dependientes como "dirty"
3. Se encolan para rerun
4. Se procesan en orden

### 5. Prevención de Ciclos

El framework detecta automáticamente ciclos:

```
A → B → C → A  ❌ CICLO DETECTADO
```

Si hay ciclo, se previene la ejecución infinita.

## 🛠️ API Completa

### @reactive_fragment(...)

Decorador para crear fragmentos reactivos.

```python
@reactive_fragment(
    dependencies=['key1', 'key2'],     # Qué observar
    watch_params=True,                 # Detectar cambios de parámetros
    prevent_cycles=True,               # Evitar loops
)
def my_fragment():
    pass
```

### register_dependency(fragment, depends_on)

Registra dependencia entre dos fragmentos DESPUÉS de decorarlos:

```python
@reactive_fragment()
def panel_a(): pass

@reactive_fragment()
def panel_b(): pass

register_dependency('panel_b', 'panel_a')  # B depende de A
```

### get_dependency_chain(fragment_name)

Obtiene todos los dependientes de un fragmento:

```python
dependents = get_dependency_chain('my_fragment')
# Retorna: {'panel_b', 'panel_c', 'panel_d', ...}
```

### enqueue_fragment_rerun(fragment_name, reason="")

Encola manualmente un fragmento:

```python
if st.button("Refrescar datos"):
    enqueue_fragment_rerun('data_panel', reason='user requested')
```

### debug_dependency_graph()

Muestra el grafo de dependencias en la UI (útil para debugging):

```python
with st.expander("🔍 Debug"):
    debug_dependency_graph()
```

### reset_reactive_state()

Limpia todo el estado reactivo (para testing):

```python
if st.button("Reset"):
    reset_reactive_state()
    st.rerun()
```

## 📊 Ejemplos Prácticos

### Ejemplo 1: Dashboard Interactivo

```python
import streamlit as st
from streamlit_plugins.framework.reactlit import reactive_fragment

@reactive_fragment(watch_params=True)
def filters():
    """Panel de filtros"""
    category = st.selectbox("Categoría", ["A", "B", "C"])
    st.session_state.selected_category = category

@reactive_fragment(dependencies=['selected_category'])
def load_data():
    """Carga datos según filtros"""
    category = st.session_state.selected_category
    
    # Simula carga
    data = [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
    ]
    
    st.session_state.table_data = data

@reactive_fragment(dependencies=['table_data'])
def display_table():
    """Muestra tabla"""
    data = st.session_state.get('table_data', [])
    st.dataframe(data)

# Main
st.title("Dashboard")
filters()
load_data()
display_table()
```

### Ejemplo 2: Form Validation

```python
from streamlit_plugins.framework.reactlit.advanced_patterns import (
    ReactiveForm
)

# Crear formulario
form = ReactiveForm(initial_values={
    'email': '',
    'password': '',
})

# Agregar campos
form.add_field('email', 'email')
form.add_field('password', 'text')

# Agregar validadores
def validate_email(value):
    if '@' not in value:
        return "Email inválido"
    return None

form.add_validator('email', validate_email)

# Renderizar
if form.render():
    st.success("Formulario válido!")
    st.json(form.values)
```

### Ejemplo 3: State Machine

```python
from streamlit_plugins.framework.reactlit.advanced_patterns import (
    FragmentStateMachine
)

fsm = FragmentStateMachine()

# Definir estados
fsm.add_state('loading', render=lambda: st.info("Cargando..."))
fsm.add_state('ready', render=lambda: st.success("Listo!"))
fsm.add_state('error', render=lambda: st.error("Error!"))

# Transicionar
if st.button("Cargar"):
    fsm.transition('loading')

if st.button("Completar"):
    fsm.transition('ready')

# Renderizar estado actual
if fsm.current_state:
    fsm.render()
```

## 🏗️ Patrones Avanzados

### Patrón 1: Cascada Lineal

```
Input → Procesar → Analizar → Visualizar
```

```python
@reactive_fragment(watch_params=True)
def input_panel(): pass

@reactive_fragment(dependencies=['input_data'])
def processor(): pass

@reactive_fragment(dependencies=['processed_data'])
def analyzer(): pass

@reactive_fragment(dependencies=['analysis'])
def visualizer(): pass
```

### Patrón 2: Árbol de Dependencias

```
        Root
       /    \
    Left   Right
    / \      |
   A   B     C
```

```python
@reactive_fragment()
def root(): pass

@reactive_fragment(dependencies=['root'])
def left(): pass

@reactive_fragment(dependencies=['left'])
def a(): pass

@reactive_fragment(dependencies=['left'])
def b(): pass

@reactive_fragment(dependencies=['root'])
def right(): pass

@reactive_fragment(dependencies=['right'])
def c(): pass
```

### Patrón 3: Store Centralizado (Redux-like)

```python
from streamlit_plugins.framework.reactlit.advanced_patterns import (
    ReactiveStore, Action
)

# Crear store
store = ReactiveStore()

# Definir acciones
store.define_action(
    'INCREMENT',
    lambda state, amt: {
        **state,
        'counter': state.get('counter', 0) + amt
    }
)

# Usar store
if st.button("Incrementar"):
    store.dispatch(Action('INCREMENT', {'amt': 1}))

st.metric("Counter", store.get('counter', 0))
```

## 🔍 Debugging

### Ver Estado del Grafo

```python
from streamlit_plugins.framework.reactlit import debug_dependency_graph

with st.expander("📊 Dependency Graph"):
    debug_dependency_graph()
```

### Ver Logs

```python
logs = st.session_state.get('_reactive_framework_log', [])
for log in logs[-10:]:  # Últimos 10 logs
    st.text(log)
```

### Ver Estado de un Fragmento

```python
from streamlit_plugins.framework.reactlit import get_fragment_state

state = get_fragment_state('my_fragment')
st.json(state)
```

## ⚙️ Configuración

### Deshabilitar Watch Params

Si no necesitas detectar cambios de parámetros:

```python
@reactive_fragment(watch_params=False)
def my_fragment(data):
    # No se rerunnea si 'data' cambia como parámetro
    pass
```

### Deshabilitar Prevención de Ciclos

Avanzado - úsalo solo si sabes lo que haces:

```python
@reactive_fragment(prevent_cycles=False)
def risky_fragment():
    pass
```

## 🚨 Limitaciones Conocidas

1. **Streamlit Fragment Limitation**: Solo un fragmento puede rerun por iteración
   - **Solución**: El framework los encola y procesa secuencialmente

2. **Session State Compartido**: Todos ven el mismo estado
   - **Solución**: Usar nombres prefijados como `_fragmento_name_key`

3. **Delta Path Estático**: No puedes cambiar dónde se renderiza
   - **Solución**: Definir layout ANTES de los fragmentos

4. **Performance con muchos fragmentos**: 100+ fragmentos puede ser lento
   - **Solución**: Usar `watch_params=False` donde no sea necesario

## 📋 Checklist de Buenas Prácticas

- [ ] Nombra fragmentos descriptivamente (`load_users`, `render_chart`)
- [ ] Observa solo lo que necesitas en `dependencies`
- [ ] Usa `watch_params=False` si no necesitas detectar cambios
- [ ] Mantén fragmentos pequeños y enfocados
- [ ] Documenta las dependencias con comentarios
- [ ] Usa `debug_dependency_graph()` en desarrollo
- [ ] Prueba ciclos con `has_dependency_cycle()`
- [ ] Prefija estado privado con `_` para evitar colisiones

## 🔧 Desarrollo

### Ejecutar Ejemplos

```bash
# Ejemplo básico
streamlit run streamlit_plugins/framework/reactlit/examples_basic.py

# Patrones avanzados
streamlit run streamlit_plugins/framework/reactlit/advanced_patterns.py
```

### Testing

```python
from streamlit_plugins.framework.reactlit import reset_reactive_state

def test_my_fragment():
    reset_reactive_state()
    # ... tu test aquí
```

## 📚 Recursos Adicionales

- **REACTIVE_DOCS.md**: Documentación técnica completa
- **advanced_patterns.py**: Implementaciones de Redux, Forms, State Machines
- **examples_basic.py**: Ejemplos sencillos para empezar

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios mayores:

1. Fork el repo
2. Crea una rama (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -am 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing`)
5. Abre un Pull Request

## 📝 Licencia

MIT - Ver LICENSE para detalles

---

**¿Preguntas?** Abre un issue o consulta la documentación técnica en REACTIVE_DOCS.md

