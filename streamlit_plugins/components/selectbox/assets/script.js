export default function (component) {
  const { key, name, data, setTriggerValue, setStateValue, parentElement } = component;
  const options = data.options || [];

  const startIndex = Number(data.index || 0);
  const placeholder = String(data.placeholder || "Choose an option");
  const acceptNew = !!data.accept_new_options;
  const disabled = !!data.disabled;
  const help = data.help || "";

  // colores map (igual que en Python) - ahora solo lista de keys usadas para generar clases
  const COLORS = {
    red: true,
    orange: true,
    yellow: true,
    green: true,
    blue: true,
    violet: true,
    gray: true,
    grey: true,
    primary: true,
    rainbow: true,
  };

  // convierte shortcodes a HTML inline -> ahora usa clases que mapearán a CSS variables
  function convertShortcodes(s) {
    if (s === null || s === undefined) return "";
    s = String(s);

    // badge :color-badge[text] -> usa .badge .badge--{color}
    s = s.replace(/:([a-zA-Z]+)-badge\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      if (COLORS[c]) {
        return `<span class="badge badge--${c}">${escapeHtml(text)}</span>`;
      }
      return `<span class="badge">${escapeHtml(text)}</span>`;
    });

    // background :color-background[text] -> usa .bg .bg--{color}
    s = s.replace(/:([a-zA-Z]+)-background\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      if (COLORS[c]) {
        return `<span class="bg bg--${c}">${escapeHtml(text)}</span>`;
      }
      return `<span class="bg">${escapeHtml(text)}</span>`;
    });

    // color[text] -> usa .text .text--{color} si es un color conocido, sino devuelve el texto sin estilo
    s = s.replace(/:([a-zA-Z]+)\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      if (COLORS[c]) {
        return `<span class="text text--${c}">${escapeHtml(text)}</span>`;
      }
      // fallback: no clase para colores desconocidos (evita estilos inline)
      return `<span>${escapeHtml(text)}</span>`;
    });

    // small
    s = s.replace(
      /:small\[(.*?)\]/g,
      (m, text) => `<small>${escapeHtml(text)}</small>`
    );

    // material icon
    s = s.replace(
      /:material\/([a-z_0-9]+):/g,
      (m, icon) => `<span class="material-icon">${escapeHtml(icon)}</span>`
    );

    return s;
  }

  // simple escaper for inserted text (we escape inside innerHTML contexts)
  function escapeHtml(unsafe) {
    return String(unsafe)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Registrar un listener local UNA sola vez para capturar SET_THEME_CONFIG
  // if (!window.__st_quiz_set_theme_listener_installed) {
  //   window.__st_quiz_set_theme_listener_installed = true;
  //   window.addEventListener("message", function (event) {
  //     try {
  //       const message = event && event.data;
  //       console.log("Mensaje recibido en selectbox:", message.type);
  //       if (message && message.type === "SET_THEME_CONFIG") {
  //         // themeInfo contiene los datos de tema
  //         // {x
  //         //   "primaryColor": "#ff4b4b",
  //         //   "backgroundColor": "#0e1117",
  //         //   "secondaryBackgroundColor": "#262730",
  //         //   "textColor": "#fafafa",
  //         //   "bodyFont": "\"Source Sans\", sans-serif",
  //         //   "base": "dark",
  //         //   "fadedText05": "rgba(250, 250, 250, 0.1)",
  //         //   "fadedText10": "rgba(250, 250, 250, 0.2)",
  //         //   "fadedText20": "rgba(250, 250, 250, 0.3)",
  //         //   "fadedText40": "rgba(250, 250, 250, 0.4)",
  //         //   "fadedText60": "rgba(250, 250, 250, 0.6)",
  //         //   "bgMix": "rgba(26, 28, 36, 1)",
  //         //   "darkenedBgMix100": "hsla(228, 16%, 72%, 1)",
  //         //   "darkenedBgMix25": "rgba(172, 177, 195, 0.25)",
  //         //   "darkenedBgMix15": "rgba(172, 177, 195, 0.15)",
  //         //   "lightenedBg05": "hsla(220, 24%, 10%, 1)"
  //         // }
  //         // console.log("Captured SET_THEME_CONFIG:", message.themeInfo, message);
  //       }
  //     } catch (e) {
  //       console.error("Error al loguear SET_THEME_CONFIG:", e);
  //     }
  //   });
  // }

  const root = parentElement.querySelector(".custom-select-root");
  const btn = root.querySelector(".select-btn");
  const helpElement = root.querySelector(".help-wrap");
  const list = root.querySelector(".select-list");

  if (help) {
    helpElement.innerHTML = help;
  }
  if (disabled) {
    btn.setAttribute("disabled", "true");
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

  options.forEach((html, i) => {
    const li = document.createElement("li");
    li.className = "select-item";
    li.setAttribute("role", "option");
    li.setAttribute("data-index", String(i));
    li.innerHTML = convertShortcodes(html);
    if (!disabled) {
      li.addEventListener("click", (e) => {
        e.stopPropagation();
        btn.innerHTML = li.innerHTML;
        hideList();
        try {
          setTriggerValue("selected", String(i));
          setStateValue("selected", String(i));
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
    btn.innerHTML = convertShortcodes(options[startIndex]);
  } else {
    btn.innerHTML = placeholder;
  }

  // make root focusable so we can use focusout instead of a document-level listener
  if (!root.hasAttribute("tabindex")) {
    root.setAttribute("tabindex", "0");
  }

  // helper: ensure we only install per-instance handlers once
  // use properties on DOM nodes to avoid global variables and duplicated listeners on re-run
  if (!disabled) {
    // btn click toggles the list; guard to avoid double-binding on re-runs
    if (!btn.__st_select_btn_click_installed) {
      btn.__st_select_btn_click_installed = true;
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = list.style.display === "block";
        if (isOpen) {
          hideList();
          btn.blur();
        } else {
          list.style.display = "block";
          // focus root so focusout will fire when focus leaves
          root.focus();
        }
      });
    }

    // avoid adding a global document click listener; use focusout on the component root
    if (!root.__st_select_focusout_installed) {
      root.__st_select_focusout_installed = true;
      root.addEventListener("focusout", (e) => {
        // relatedTarget is the element receiving focus; if it's outside root, hide
        const related = e.relatedTarget;
        if (!root.contains(related)) {
          hideList();
        }
      });

      // optionally allow Esc to close the list
      root.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          hideList();
          btn.blur();
        }
      });
    }
  }
}
