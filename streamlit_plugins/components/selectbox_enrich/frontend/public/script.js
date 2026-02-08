export default function (component) {
  const { key, name, data, setTriggerValue, setStateValue, parentElement } = component;
  const options = data.options || [];

  let startIndex = Number(data.index || 0);
  const label = String(data.label || "");
  const labelVisibility = String(data.labelVisibility || "visible");
  const placeholder = String(data.placeholder || "Choose an option");
  const acceptNew = !!data.acceptNewOptions;
  const unsafeAllowHtml = !!data.unsafeAllowHtml;
  const disabled = !!data.disabled;
  const help = data.help || "";

  // Remover listeners previos si existen para evitar duplicados
  const root = parentElement.querySelector(".custom-select-root");
  if (!root) {
    console.error("No se encontró .custom-select-root");
    return;
  }

  // se agrega el attributo disabled
  if (disabled) {
    root.setAttribute("disabled", "true");
  }
  else {
    root.removeAttribute("disabled");
  }
  
  // Limpiar listeners previos
  if (root._docClickListener) {
    document.removeEventListener("click", root._docClickListener);
  }

  // convierte shortcodes a HTML inline
  function convertShortcodes(s, allowHtml = false) {
    if (s === null || s === undefined) return "";
    s = String(s);
    let color = "";
    // badge :color-badge[text]
    s = s.replace(/:([a-zA-Z]+)-badge\[(.*?)\]/g, (m, color, text) => {
      color = color.toLowerCase();
      return `<span class="badge ${color}">${escapeHtml(text, allowHtml)}</span>`;
    });

    // background :color-background[text]
    s = s.replace(/:([a-zA-Z]+)-background\[(.*?)\]/g, (m, color, text) => {
      color = color.toLowerCase();
      return `<span class="bg ${color}">${escapeHtml(text, allowHtml)}</span>`;
    });

    // color[text]
    s = s.replace(/:([a-zA-Z]+)\[(.*?)\]/g, (m, color, text) => {
      color = color.toLowerCase();
      return `<span class="color ${color}">${escapeHtml(text, allowHtml)}</span>`;
    });
    // small
    s = s.replace(
      /:small\[(.*?)\]/g,
      (m, text) => `<small>${escapeHtml(text, allowHtml)}</small>`
    );

    // ***bold+italic***, es negrita + italico
    s = s.replace(/\*\*\*([^*\n]+)\*\*\*/g, (m, text) => `<strong><em>${escapeHtml(text, allowHtml)}</em></strong>`);
    
    // **strong**, es negrita
    s = s.replace(/\*\*([^*\n]+)\*\*/g, (m, text) => `<strong>${escapeHtml(text, allowHtml)}</strong>`);
    
    // *emphasis*, es italico
    s = s.replace(/\*([^*\n]+)\*/g, (m, text) => `<em>${escapeHtml(text, allowHtml)}</em>`);

    // material icon
    s = s.replace(
      /:material\/([a-z_0-9]+):/g,
      (m, icon) => `<span class="material-symbols-rounded">${escapeHtml(icon)}</span>`
    );

    return s;
  }

  // simple escaper for inserted text (we escape inside innerHTML contexts)
  function escapeHtml(unsafe, allowHtml = false) {
    if (allowHtml) return String(unsafe);
    return String(unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  startIndex = root.dataset.selectedIndex || startIndex;

  const selectContainer = root.querySelector(".select-content-container");
  const selectContent = root.querySelector(".select-content");
  const labelElement = root.querySelector(".select-label span");
  const helpElement = root.querySelector(".help-tooltip .help-content");
  const list = root.querySelector(".select-list");
  if (label) {
    labelElement.textContent = label;
  }
  if (labelVisibility) {
    if (labelVisibility === "hidden") {
      labelElement.style.display = "none";
    } else if (labelVisibility === "visible") {
      labelElement.style.display = "flex";
    } else if (labelVisibility === "collapsed") {
      labelElement.style.display = "flex";
      labelElement.style.position = "absolute";
      labelElement.style.left = "-9999px";
    }
  }
  if (help) {
    helpElement.innerHTML = help;
  }
  if (disabled) {
    selectContainer.setAttribute("disabled", "true");
  }

  // helper para cerrar
  function hideList() {
    list.style.display = "none";
  }

  // construir UI
  list.innerHTML = "";

  if (acceptNew) {
    const addWrap = document.createElement("div");
    addWrap.className = "select-add";
    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Añadir nueva opción...";
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && input.value.trim()) {
        const v = input.value.trim();
        try {
          setTriggerValue("new::" + v);
        } catch (e) {
          window.parent.postMessage(
            { type: "html_select_selected", value: "new::" + v },
            "*"
          );
        }
        input.value = "";
      }
    });
    const btnAdd = document.createElement("button");
    btnAdd.textContent = "+";
    btnAdd.onclick = () => {
      if (input.value.trim()) {
        const v = input.value.trim();
        try {
          setTriggerValue("new::" + v);
        } catch (e) {
          window.parent.postMessage(
            { type: "html_select_selected", value: "new::" + v },
            "*"
          );
        }
        input.value = "";
      }
    };
    addWrap.appendChild(input);
    addWrap.appendChild(btnAdd);
    list.appendChild(addWrap);
  }

  options.forEach((contentValue, i) => {
    const li = document.createElement("li");
    li.className = "select-item";
    li.setAttribute("role", "option");
    li.setAttribute("data-index", String(i));
    li.innerHTML = convertShortcodes(contentValue, unsafeAllowHtml);
    if (!disabled) {
      li.addEventListener("click", (e) => {
        e.stopPropagation();
        selectContent.innerHTML = li.innerHTML;
        hideList();
        try {
          setTriggerValue("selected", String(i));
          setStateValue("selected", String(i));
          root.dataset.selectedIndex = String(i);
        } catch (err) {
          window.parent.postMessage(
            { type: "html_select_selected", value: String(i) },
            "*"
          );
        }
      });
    }
    list.appendChild(li);
  });

  // inicializar texto del botón
  if (options[startIndex]) {
    selectContent.innerHTML = convertShortcodes(options[startIndex]);
  } else {
    selectContent.innerHTML = placeholder;
  }
  
  if (!disabled) {
    // Crear y guardar el listener del botón para evitar duplicados
    const btnClickListener = (e) => {
      e.stopPropagation();
      // Si el root esta disabled, no hacer nada
      if (root.hasAttribute("disabled")) return;
      list.style.display = list.style.display === "block" ? "none" : "block";
    };
    
    // Remover listener previo si existe
    if (selectContainer._clickListener) {
      selectContainer.removeEventListener("click", selectContainer._clickListener);
    }
    
    selectContainer._clickListener = btnClickListener;
    selectContainer.addEventListener("click", btnClickListener);
    
    // Remover listener de documento previo si existe
    if (root._docClickListener) {
      document.removeEventListener("click", root._docClickListener);
    }
    
    // Crear y guardar el listener del documento para evitar duplicados
    const docClickListener = (e) => {
      if (!root.contains(e.target)) hideList();
    };
    
    root._docClickListener = docClickListener;
    document.addEventListener("click", docClickListener);
  }
  
  // Marcar como inicializado
  root.setAttribute("data-initialized", "true");
}
