# 🔗 Guía de Integración - Reactlit en Streamlit-Plugins

## 📍 Ubicación en el Proyecto

```
streamlit-plugins/
└── streamlit_plugins/
    └── framework/
        ├── multilit/          (existente)
        │   └── ...
        └── reactlit/          (✅ NUEVO)
            ├── __init__.py               (exportaciones públicas)
            ├── reactive.py               (⭐ CORE - 17KB)
            ├── advanced_patterns.py      (patrones avanzados - 19KB)
            ├── README.md                 (guía de usuario)
            ├── QUICK_START.md            (inicio rápido)
            ├── REACTIVE_DOCS.md          (referencia técnica)
            ├── ARCHITECTURE.md           (arquitectura interna)
            ├── SUMMARY.md                (resumen completo)
            ├── examples_basic.py         (ejemplo simple)
            ├── example_dashboard.py      (ejemplo real)
            └── test_reactive.py          (suite de tests)
```

## 🔀 Relación con Otros Componentes

### vs. Multilit

```
Multilit:
  └─ Multi-página routing
  └─ Navegación de apps
  └─ Dashboards estáticos

Reactlit: (NUEVO)
  └─ Reactitividad dentro de página
  └─ Componentes interactivos
  └─ State management dinámico

COMBINACIÓN:
  Multilit (routing) + Reactlit (reactivity) = Super App!
```

### vs. Componentes Existentes

```
Navbar:
  └─ UI/UX - Navegación top
  
Reactlit: (COMPLEMENTARIO)
  └─ State Management - Lógica de app
  
Pueden usarse juntos!
```

## 💻 Cómo Usar en Tu Proyecto

### Opción 1: Uso Básico

```python
# app.py
from streamlit_plugins.framework.reactlit import reactive_fragment

@reactive_fragment(dependencies=['data'])
def my_component():
    st.write("Componente reactivo")

# Ejecuta normalmente
my_component()
```

### Opción 2: Con Multilit

```python
# apps/dashboard.py
from streamlit_plugins.framework.reactlit import reactive_fragment

@reactive_fragment(dependencies=['filters'])
def dashboard_content():
    st.title("Mi Dashboard")
    # Contenido reactivo aquí

# En main.py de multilit
from apps.dashboard import dashboard_content
dashboard_content()
```

### Opción 3: Arquitectura Escalada

```python
# lib/fragments.py
from streamlit_plugins.framework.reactlit import reactive_fragment

@reactive_fragment(dependencies=['user_id'])
def user_panel(user_id):
    st.write(f"Usuario: {user_id}")

@reactive_fragment(dependencies=['user_data'])
def stats_panel():
    st.write("Estadísticas")

# app.py
from lib.fragments import user_panel, stats_panel

user_panel(st.session_state.selected_user)
stats_panel()
```

## 📦 Instalación / Setup

### Ya Incluido

```bash
# El framework ya está en el workspace
# Solo importa:
from streamlit_plugins.framework.reactlit import reactive_fragment
```

### Si es Necesario Reinstalar

```bash
cd D:\workspace\Projects\streamlit-plugins
pip install -e .
```

## 🚀 Primeros Pasos en Tu Proyecto

### Step 1: Ejecutar Ejemplos

```bash
# Ejemplo básico
streamlit run streamlit_plugins/framework/reactlit/examples_basic.py

# Ejemplo real
streamlit run streamlit_plugins/framework/reactlit/example_dashboard.py
```

### Step 2: Entender Conceptos

Lee en este orden:
1. `QUICK_START.md` (5 min) - Conceptos básicos
2. `README.md` (10 min) - API completa
3. `example_dashboard.py` (10 min) - Código real

### Step 3: Crear Primer Componente

```python
# my_first_reactive.py
import streamlit as st
from streamlit_plugins.framework.reactlit import reactive_fragment

st.title("Mi Primera App Reactiva")

@reactive_fragment(watch_params=True)
def input_panel():
    st.session_state.value = st.slider("Valor:", 0, 100)

@reactive_fragment(dependencies=['value'])
def output_panel():
    v = st.session_state.get('value', 0)
    st.metric("Cuadrado", v**2)

input_panel()
output_panel()
```

Ejecutar:
```bash
streamlit run my_first_reactive.py
```

## 🔧 Integración con Multilit

```python
# En pages/dashboard.py de multilit

import streamlit as st
from streamlit_plugins.framework.reactlit import reactive_fragment

# Registra como página normal
st.title("Dashboard Reactivo")

@reactive_fragment(dependencies=['filters'])
def filters_panel():
    st.session_state.category = st.selectbox("Cat:", ["A", "B", "C"])

@reactive_fragment(dependencies=['category'])
def data_panel():
    cat = st.session_state.category
    st.write(f"Datos de {cat}")

# Ejecuta
filters_panel()
data_panel()
```

El multilit hace routing, Reactlit hace reactividad.

## 📊 Arquitectura Recomendada

Para proyectos medianos/grandes:

```
app/
├── pages/
│   ├── dashboard.py          (usa Reactlit para reactividad)
│   ├── analytics.py          (usa Reactlit para reactividad)
│   └── settings.py           (usa Reactlit para formularios)
│
├── lib/
│   ├── fragments/            (tus componentes reactivos)
│   │   ├── filters.py        (@reactive_fragment)
│   │   ├── charts.py         (@reactive_fragment)
│   │   └── tables.py         (@reactive_fragment)
│   │
│   ├── stores/               (estado compartido)
│   │   ├── app_store.py      (ReactiveStore)
│   │   └── user_store.py     (ReactiveStore)
│   │
│   └── utils/
│       ├── data.py           (carga de datos)
│       └── validators.py     (validación)
│
└── main.py                   (app principal con Multilit)
```

## 🎨 Patrones de Integración

### Patrón 1: Simple (Starter)

```python
@reactive_fragment(watch_params=True)
def main():
    # Todo aquí
    st.write("Mi app")

main()
```

### Patrón 2: Modular (Growth)

```python
@reactive_fragment(dependencies=['data'])
def component_a():
    pass

@reactive_fragment(dependencies=['data'])
def component_b():
    pass

st.columns(2)  # Layout
```

### Patrón 3: Con Store (Scale)

```python
from streamlit_plugins.framework.reactlit.advanced_patterns import (
    ReactiveStore
)

store = ReactiveStore()
# Usa store para estado global
```

### Patrón 4: Completo (Enterprise)

```python
# 1. Fragmentos modularizados
from lib.fragments import *

# 2. Store centralizado
from lib.stores import app_store

# 3. Lazy loading
import importlib

# 4. Testing
from tests import *
```

## 🔗 Exportaciones Disponibles

```python
# Lo que puedes importar:
from streamlit_plugins.framework.reactlit import (
    # Decorador
    reactive_fragment,
    
    # Registro
    register_dependency,
    register_dependencies,
    
    # Consultas
    get_fragment_metadata,
    get_all_fragments,
    get_dependency_chain,
    has_dependency_cycle,
    
    # Utilidades
    get_fragment_state,
    set_fragment_dirty,
    enqueue_fragment_rerun,
    manually_trigger_rerun_cascade,
    
    # Debug
    debug_dependency_graph,
    reset_reactive_state,
    
    # Data Models
    FragmentMetadata,
    DependencyGraph,
)
```

## 🧪 Testing Tu Integración

```python
# test_my_integration.py
from streamlit_plugins.framework.reactlit import reset_reactive_state

def test_my_fragment():
    reset_reactive_state()
    # Tu test aquí
```

## 📈 Performance Tips

Para apps grandes:

```python
# ✅ Bien - Fragmentos pequeños y enfocados
@reactive_fragment(dependencies=['user_id'])
def load_user():
    pass

# ❌ Evitar - Fragmentos que hacen todo
@reactive_fragment(dependencies=['everything'])
def mega_fragment():
    pass
```

## 🐛 Debugging en Desarrollo

```python
# Añade esto en development:
if st.session_state.get('DEBUG_MODE'):
    with st.expander("🔍 Debug"):
        debug_dependency_graph()
```

## 🚨 Problemas Comunes en Integración

### Problema 1: State no sincronizado

```python
# ❌ Error
st.session_state.data = []
st.session_state.data.append(1)  # In-place mutation

# ✅ Solución
st.session_state.data = st.session_state.data + [1]  # Reasignar
```

### Problema 2: Fragmentos no registrados

```python
# ✅ Siempre decorar
@reactive_fragment()
def mi_funcion():
    pass

# ❌ Nunca olvidar el decorador
def mi_funcion():
    pass
```

### Problema 3: Ciclos accidentales

```python
# El framework lo previene automáticamente
# Pero evita estas estructuras intencionalmente
```

## 📚 Recursos Adicionales

### En el Repo

- `README.md` - Documentación completa
- `QUICK_START.md` - Inicio rápido
- `ARCHITECTURE.md` - Detalles técnicos
- `REACTIVE_DOCS.md` - Referencia API
- `example_dashboard.py` - Ejemplo real
- `test_reactive.py` - Tests

### Documentación Externa

- Streamlit Docs: https://docs.streamlit.io/
- React Hooks (inspiración): https://react.dev/reference/react

## ✅ Checklist de Integración

- [ ] Ejecuté `examples_basic.py`
- [ ] Ejecuté `example_dashboard.py`
- [ ] Leí `QUICK_START.md`
- [ ] Creé mi primer componente reactivo
- [ ] Lo integré en mi app
- [ ] Pasó los tests básicos
- [ ] Configuré debug si es necesario
- [ ] Documenté mis fragmentos

## 🤝 Integración con CI/CD

```bash
# En tu pipeline de CI/CD

# Lint
pylint streamlit_plugins/framework/reactlit/

# Tests
pytest streamlit_plugins/framework/reactlit/test_reactive.py

# Type Check
mypy streamlit_plugins/framework/reactlit/reactive.py
```

## 🔮 Roadmap de Desarrollo

Ideas para mejorar la integración:

- [ ] CLI de generación de fragmentos
- [ ] IDE plugin para autocompletar dependencias
- [ ] DevTools visual integrados
- [ ] Profiling automático de performance
- [ ] Integración con linters personalizados

## 📞 Soporte Técnico

Para preguntas sobre integración:

1. Revisa la documentación (archivos .md)
2. Analiza los ejemplos
3. Consulta el código fuente (reactive.py)
4. Ejecuta tests para validar

---

**¡Tu integración está lista!** 🎉

Próximo paso: Ejecuta un ejemplo y comienza a crear fragmentos reactivos.

