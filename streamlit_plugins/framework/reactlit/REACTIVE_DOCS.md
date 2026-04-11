"""
Advanced Reactive Fragment Framework - Documentación Técnica
=============================================================

## 🎯 CONCEPTOS FUNDAMENTALES

### 1. Fragmentos Reactivos
Un fragmento reactivo es un componente aislado que:
- Se renderiza de forma independiente
- Observa cambios en dependencias específicas
- Dispara cascadas de reruns automáticamente
- Mantiene su propio estado

### 2. Dependencias
Hay dos tipos de dependencias:
- **Externas**: Session state keys que el fragmento observa
- **Internas**: Otros fragmentos de los cuales depende

Ejemplo:
```python
@reactive_fragment(
    dependencies=['user_id', 'other_fragment'],
)
def my_fragment():
    pass
```

### 3. Cambio de Parámetros
Si `watch_params=True`, el framework detecta cuando los
parámetros de entrada cambian y marca dependientes como dirty.

### 4. Grafo de Dependencias
El framework mantiene un grafo que mapea:
- Qué fragmentos dependen de cuáles
- Las cadenas transitivas de dependencias
- Detecta ciclos para prevenir loops infinitos

---

## 📋 API REFERENCE

### @reactive_fragment(...)
Decorador para crear fragmentos reactivos.

**Parámetros:**
- `dependencies`: list[str] - Session state keys o nombres de fragmentos a observar
- `dependents`: list[str] - Fragmentos que dependen de este (opcional)
- `watch_params`: bool - Si True, detecta cambios en parámetros (default: True)
- `prevent_cycles`: bool - Si True, evita ejecutar si hay ciclos (default: True)

**Ejemplo:**
```python
@reactive_fragment(
    dependencies=['user_id', 'filters'],
    watch_params=True
)
def load_data(user_id, filters=None):
    st.write(f"Cargando datos de {user_id}")
    # El fragmento se rerunnea si user_id o filters cambian
```

### register_dependency(fragment, depends_on)
Registra una dependencia entre dos fragmentos DESPUÉS de que
ambos estén decorados.

```python
register_dependency('panel_b', 'panel_a')  # B depende de A
```

### get_dependency_chain(fragment_name)
Retorna todos los fragmentos que dependen (transitivamente)
de uno específico.

```python
dependents = get_dependency_chain('my_fragment')
# Retorna: {'panel_b', 'panel_c', 'panel_d'}
```

### enqueue_fragment_rerun(fragment_name, reason="")
Encola manualmente un fragmento para rerun.

```python
enqueue_fragment_rerun('panel_data', reason='user requested refresh')
```

### set_fragment_dirty(fragment_name, dirty=True)
Marca manualmente un fragmento como que necesita rerun.

### get_fragment_state(fragment_name)
Obtiene el estado actual (parámetros, dirty flag) de un fragmento.

### debug_dependency_graph()
Muestra en Streamlit el estado completo del grafo de dependencias.

### reset_reactive_state()
Limpia todo el estado reactivo (útil para testing).

---

## 🔄 FLUJO DE EJECUCIÓN

1. **Renderizado inicial**
   - Todos los fragmentos se ejecutan normalmente
   - Se registran en el grafo de dependencias
   - Se capturan los parámetros iniciales

2. **Detección de cambios**
   - Si un widget dentro de un fragmento cambia
   - Se comparar con última ejecución
   - Si hay cambios, se marca el fragmento como dirty

3. **Propagación a dependientes**
   - Se identifica toda la cadena de dependientes
   - Se marca cada uno como dirty
   - Se encolan para próximo rerun

4. **Evitación de ciclos**
   - Si hay ciclo: A → B → C → A
   - El framework detecta y previene ejecución infinita
   - Se puede configurar con `prevent_cycles=True`

5. **Rerun fragmentado**
   - Se procesa la cola de fragmentos
   - Se dispara rerun para cada uno
   - Se vuelve al paso 2

---

## 💡 PATRONES COMUNES

### Patrón 1: Cascada Lineal
```
Controles → Datos → Análisis → Gráficos
```

```python
@reactive_fragment(dependencies=['category', 'date_range'])
def controls():
    # Panel de entrada
    pass

@reactive_fragment(dependencies=['category', 'date_range'])
def load_data():
    # Carga datos según controles
    pass

@reactive_fragment(dependencies=['data'])
def analyze():
    # Analiza los datos
    pass

@reactive_fragment(dependencies=['analysis'])
def visualize():
    # Muestra gráficos
    pass
```

### Patrón 2: Árbol de Dependencias
```
       Root
      /    \
   Left   Right
   /  \     |
  A    B    C
```

```python
@reactive_fragment()
def root():
    pass

@reactive_fragment(dependencies=['root'])
def left():
    pass

@reactive_fragment(dependencies=['root'])
def right():
    pass

@reactive_fragment(dependencies=['left'])
def a():
    pass

@reactive_fragment(dependencies=['left'])
def b():
    pass

@reactive_fragment(dependencies=['right'])
def c():
    pass
```

### Patrón 3: Con Estado Compartido
```python
@reactive_fragment()
def input_panel():
    val = st.slider("Valor:", 0, 100)
    st.session_state.shared_value = val
    
    # Esto marca automáticamente los dependientes

@reactive_fragment(dependencies=['shared_value'])
def processor():
    val = st.session_state.shared_value
    result = val * 2
    st.session_state.processed = result

@reactive_fragment(dependencies=['processed'])
def output():
    st.metric("Resultado", st.session_state.processed)
```

### Patrón 4: Prevención de Ciclos
```python
@reactive_fragment(prevent_cycles=True)
def fragA():
    if st.button("Trigger B"):
        enqueue_fragment_rerun('fragB')

@reactive_fragment(prevent_cycles=True)
def fragB():
    if st.button("Trigger A"):
        enqueue_fragment_rerun('fragA')
    # fragB no se ejecutará de nuevo si está en cola de A
```

### Patrón 5: Observación de Parámetros
```python
@reactive_fragment(watch_params=True)
def processor(data, threshold=0.5):
    # Si data o threshold cambian como parámetros
    # DENTRO del wrapper, se detecta y marca dirty
    st.write(f"Data: {len(data) if data else 0}")
    st.write(f"Threshold: {threshold}")
```

---

## 🛡️ MANEJO DE ERRORES Y EDGE CASES

### Ciclos Infinitos
El framework:
1. Detecta ciclos automáticamente con `has_cycle()`
2. No ejecuta fragmentos que crearían ciclos
3. Registra en logs cuándo se detecta un ciclo

### Fragmentos que no existen
```python
enqueue_fragment_rerun('nonexistent')  # Safe - no lanza excepción
```

### Session state desincronizado
- Cada fragmento mantiene su propia copia de parámetros
- Se compara contra última ejecución
- Si hay desincronización, se fuerza rerun

### State explosion (muchos fragmentos)
El grafo es eficiente para hasta 100+ fragmentos.
Para millones de relaciones, considerar sharding.

---

## 🐛 DEBUGGING

### Ver el Grafo Completo
```python
debug_dependency_graph()  # Muestra en la UI
```

### Logs Internos
```python
st.session_state._reactive_framework_log
# Muestra eventos recientes: queues, cambios, ciclos, etc
```

### State por Fragmento
```python
from streamlit_plugins.framework.reactlit.reactive import get_fragment_state

state = get_fragment_state('my_fragment')
# {
#   'params': {...},
#   'is_dirty': False,
#   'last_rendered_params': {...}
# }
```

---

## ⚡ OPTIMIZACIONES

### 1. Granularidad de Observación
Observa solo lo que necesitas:
```python
# ❌ Malo - Observa todo
@reactive_fragment(dependencies=['huge_dataframe'])
def processor():
    pass

# ✅ Bien - Solo observa lo que cambia
@reactive_fragment(dependencies=['user_id'])
def processor(user_id):
    pass
```

### 2. Fragmentos Pesados
Para cálculos costosos, considera caching:
```python
@reactive_fragment(dependencies=['user_id'])
def expensive_fragment(user_id):
    @st.cache_data
    def load_data(_user_id):
        return run_expensive_query(_user_id)
    
    data = load_data(user_id)
    st.write(data)
```

### 3. Control Manual de Reruns
```python
@reactive_fragment(watch_params=False)  # Desactiva auto-detection
def manual_fragment():
    if st.button("Rerun"):
        enqueue_fragment_rerun('dependent_fragment')
```

---

## 🚀 CASOS DE USO

1. **Dashboards interactivos** - Varios paneles que reaccionan a filtros
2. **Workflows multi-paso** - Pasos que dependen de anteriores
3. **Análisis exploratorio** - Cambios en un widget afectan visualizaciones
4. **Sistemas de configuración** - Cambios en settings propagan a módulos
5. **Procesamiento de datos** - Pipelines que se replantean automáticamente

---

## ⚠️ LIMITACIONES CONOCIDAS

1. **Streamlit Fragment Limitation**: Solo se puede rerun un fragmento a la vez
   - **Solución**: El framework encola y procesa secuencialmente

2. **Session State Compartido**: Todos los fragmentos ven el mismo state
   - **Solución**: Usar nombres prefijados para evitar colisiones

3. **Delta Path Estático**: No se puede cambiar dónde se renderiza un fragmento
   - **Solución**: Definir layout ANTES de los fragmentos

4. **Performance con muchos cambios**:
   - **Solución**: Usar `watch_params=False` donde no sea necesario

---

## 📝 NOTAS TÉCNICAS INTERNAS

### Almacenamiento de Metadatos

```
_GLOBAL_REGISTRY: dict[str, FragmentMetadata]
  └─ fragment_name → {
       name: str
       func: Callable
       dependencies: Set[str]
       dependents: Set[str]
       param_watchers: dict
       delta_path: str
       fragment_id: str
       is_dirty: bool
     }

_GLOBAL_GRAPH: DependencyGraph
  └─ fragments: dict (copia de registry)
  └─ rerun_queue: list[str]
  └─ visited_in_cycle_check: Set[str]

st.session_state._reactive_graph_state: dict
  └─ rerun_queue: list[str]
  └─ executing: Set[str]
  └─ last_params: dict
  └─ fragment_ids: dict
```

### Detección de Cambios

Hash-based comparison:
```
Parámetros actuales → MD5 → Comparar con último hash
Si != → Hay cambios
```

Valores específicos también se comparan directamente.

### Propagación de Dirty Flags

```
Fragment A (dirty) 
  → get_dependents_chain('A') → {B, C, D}
  → Marcar B, C, D como dirty
  → Encolar en rerun_queue
```

Usa DFS para evitar duplicados.

---

## 🔮 Roadmap Futuro

- [ ] Serialización de state entre sesiones
- [ ] Integración con Streamlit's built-in caching
- [ ] Profiling integrado de performance
- [ ] Visualización interactiva del grafo
- [ ] Soporte para async fragments
- [ ] Memoization automática de outputs
"""

# Este archivo es solo documentación
# Úsalo como referencia mientras desarrollas tus fragmentos

