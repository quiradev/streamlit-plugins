# 🚀 Quick Start - Reactlit Framework

> Empieza a crear fragmentos reactivos en 5 minutos

## ⚡ Lo Más Esencial

### 1. Instalación

Ya está instalado en tu workspace:

```python
from streamlit_plugins.framework.reactlit import reactive_fragment
```

### 2. Tu Primer Fragmento Reactivo

Crea un archivo `my_app.py`:

```python
import streamlit as st
from streamlit_plugins.framework.reactlit import reactive_fragment

st.title("Mi Primera App Reactiva")

# Fragmento 1: Input
@reactive_fragment(watch_params=True)
def controles():
    valor = st.slider("Elige un número:", 0, 100)
    st.session_state.numero = valor

# Fragmento 2: Output (depende del anterior)
@reactive_fragment(dependencies=['numero'])
def mostrar_resultado():
    num = st.session_state.get('numero', 0)
    st.write(f"Elegiste: {num}")
    st.metric("Doble", num * 2)

# Ejecuta
controles()
mostrar_resultado()
```

Corre con:
```bash
streamlit run my_app.py
```

**¡Listo!** Mueve el slider y verás que `mostrar_resultado()` se actualiza automáticamente.

## 📖 Conceptos Clave (2 minutos)

### Decorador `@reactive_fragment()`

```python
@reactive_fragment(
    dependencies=['key1', 'key2'],     # ¿Qué observar?
    watch_params=True                  # ¿Detectar cambios?
)
def my_component():
    pass
```

**Parámetros:**

| Parámetro | Qué hace |
|-----------|----------|
| `dependencies` | Lista de `session_state` keys que observa |
| `watch_params` | Si `True`, detecta cambios en parámetros |
| `dependents` | (Opcional) Qué fragmentos dependen de este |

### Tipos de Dependencias

```python
# Tipo 1: Session state key
@reactive_fragment(dependencies=['user_id'])
def panel():
    user = st.session_state.user_id

# Tipo 2: Nombre de otro fragmento
@reactive_fragment(dependencies=['panel_a'])
def panel_b():
    # Se actualiza cuando panel_a cambia
    pass
```

### Compartir Datos

```python
@reactive_fragment(watch_params=True)
def input_panel():
    valor = st.text_input("Entrada:")
    st.session_state.shared_value = valor  # Guardar

@reactive_fragment(dependencies=['shared_value'])
def output_panel():
    valor = st.session_state.get('shared_value', '')
    st.write(f"Recibí: {valor}")
```

## 🎨 Patrones Comunes

### Patrón 1: Cascada Lineal

```
Input → Procesar → Mostrar
```

```python
@reactive_fragment(watch_params=True)
def input_frag():
    st.session_state.data = st.text_input("Datos:")

@reactive_fragment(dependencies=['data'])
def process_frag():
    data = st.session_state.data
    result = data.upper()
    st.session_state.result = result

@reactive_fragment(dependencies=['result'])
def display_frag():
    st.write(st.session_state.result)

# Ejecuta en orden
input_frag()
process_frag()
display_frag()
```

### Patrón 2: Árbol (múltiples dependientes)

```
        Input
       /     \
    Panel A  Panel B
```

```python
@reactive_fragment(watch_params=True)
def input_panel():
    st.session_state.valor = st.slider("Valor:", 0, 10)

@reactive_fragment(dependencies=['valor'])
def panel_a():
    v = st.session_state.valor
    st.metric("A", v * 2)

@reactive_fragment(dependencies=['valor'])
def panel_b():
    v = st.session_state.valor
    st.metric("B", v * 3)

# Ambos se actualizan cuando 'valor' cambia
input_panel()
col1, col2 = st.columns(2)
with col1:
    panel_a()
with col2:
    panel_b()
```

## 🛠️ Debugging

### Ver qué está pasando

```python
from streamlit_plugins.framework.reactlit import debug_dependency_graph

with st.expander("🔍 Debug"):
    debug_dependency_graph()
```

### Ver estado de un fragmento

```python
from streamlit_plugins.framework.reactlit import get_fragment_state

state = get_fragment_state('my_fragment')
st.json(state)
```

## ❌ Errores Comunes

### ❌ Error 1: Ciclo Infinito

```python
@reactive_fragment(dependencies=['panel_b'])
def panel_a():
    st.session_state.x = 1

@reactive_fragment(dependencies=['panel_a'])
def panel_b():
    st.session_state.y = 1
```

**Solución**: El framework lo detecta y previene automáticamente.

### ❌ Error 2: Cambios no detectados

```python
# ❌ Esto NO es visto:
@reactive_fragment(dependencies=['users'])
def my_panel():
    users = st.session_state.users  # Observa 'users'
    if st.button("Load"):
        users.append("John")  # Modifica lista in-place
```

**Solución**: Reasignar la variable:

```python
# ✅ Correcto:
@reactive_fragment(dependencies=['users'])
def my_panel():
    users = st.session_state.users
    if st.button("Load"):
        st.session_state.users = users + ["John"]  # Reasignar
```

### ❌ Error 3: No viendo dependencia

```python
# ❌ No detecta cambios:
@reactive_fragment(watch_params=False)
def my_panel(users):
    st.write(users)

# users cambia pero no se renderiza
```

**Solución**: Activar `watch_params`:

```python
# ✅ Correcto:
@reactive_fragment(watch_params=True)
def my_panel(users):
    st.write(users)
```

## 📊 Ejemplo Real en 50 Líneas

```python
import streamlit as st
import pandas as pd
from streamlit_plugins.framework.reactlit import reactive_fragment

st.title("Analytics Real-time")

# Generar datos
@reactive_fragment(watch_params=True)
def filters():
    """Input: Filtros"""
    min_val = st.slider("Min:", 0, 50)
    max_val = st.slider("Max:", 50, 100)
    st.session_state.range = (min_val, max_val)

@reactive_fragment(dependencies=['range'])
def load_data():
    """Proceso: Cargar datos filtrados"""
    min_v, max_v = st.session_state.range
    data = pd.DataFrame({
        'value': [i for i in range(0, 100) if min_v <= i <= max_v],
        'squared': [i**2 for i in range(0, 100) if min_v <= i <= max_v],
    })
    st.session_state.data = data

@reactive_fragment(dependencies=['data'])
def show_stats():
    """Output: Mostrar estadísticas"""
    data = st.session_state.data
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Count", len(data))
    with col2:
        st.metric("Avg", data['value'].mean():.0f)
    st.line_chart(data.set_index('value')['squared'])

# Ejecuta
filters()
load_data()
show_stats()
```

## 🚀 Próximos Pasos

1. **Ejecuta ejemplos**:
   ```bash
   streamlit run streamlit_plugins/framework/reactlit/examples_basic.py
   streamlit run streamlit_plugins/framework/reactlit/example_dashboard.py
   ```

2. **Crea tu propia app** usando los patrones aquí

3. **Explora patrones avanzados** en `advanced_patterns.py`:
   - Redux Store
   - Formularios reactivos
   - State machines
   - Inyección de dependencias

4. **Lee la documentación**:
   - `README.md` - Guía completa
   - `REACTIVE_DOCS.md` - Referencia técnica
   - `ARCHITECTURE.md` - Cómo funciona internamente

## 💡 Tips Pro

### Tip 1: Usa nombres descriptivos

```python
# ❌ Malo
@reactive_fragment(dependencies=['d'])
def f():
    pass

# ✅ Bien
@reactive_fragment(dependencies=['user_data'])
def render_user_profile():
    pass
```

### Tip 2: Observa solo lo necesario

```python
# ❌ Mal - Observa todo
@reactive_fragment(dependencies=['huge_dataframe'])
def my_panel():
    pass

# ✅ Bien - Solo lo necesario
@reactive_fragment(dependencies=['user_id'])
def load_user_data(user_id):
    pass
```

### Tip 3: Desactiva watch_params si no la necesitas

```python
# Solo rerun si sesión state cambia
@reactive_fragment(watch_params=False)
def static_content():
    st.write("I only update when session state changes")
```

### Tip 4: Agrupa datos relacionados

```python
# ❌ Muchas claves
st.session_state.user_name = "John"
st.session_state.user_email = "john@example.com"
st.session_state.user_age = 30

# ✅ Mejor - Una sola clave
st.session_state.user = {
    'name': 'John',
    'email': 'john@example.com',
    'age': 30
}
```

## 🎯 Casos de Uso Perfectos

- ✅ Dashboards con múltiples gráficos
- ✅ Forms con validación en vivo
- ✅ Data pipelines interactivos
- ✅ Analytics tools
- ✅ Configuration panels
- ✅ Real-time monitoring

## ❓ FAQ Rápido

**P: ¿Puedo usar hooks de React?**
R: No, este es Streamlit. Pero `@reactive_fragment` es similar.

**P: ¿Qué pasa si hay ciclos?**
R: El framework los detecta y previene automáticamente.

**P: ¿Es más rápido que st.rerun()?**
R: Sí, solo rerunnea lo necesario.

**P: ¿Puedo mezclar con código normal?**
R: Sí, funciona perfectamente con Streamlit estándar.

**P: ¿Cuál es el overhead?**
R: Muy bajo, ~1KB por fragmento registrado.

## 📞 Necesitas Ayuda?

1. Revisa los ejemplos incluidos
2. Lee `README.md`
3. Consulta `REACTIVE_DOCS.md`
4. Ejecuta `debug_dependency_graph()`

---

**¡Ya estás listo!** Crea tu primer fragmento reactivo ahora 🚀

