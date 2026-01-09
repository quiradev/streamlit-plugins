export default function (component) {
  const { key, name, data, setTriggerValue, setStateValue, parentElement } = component;
  const options = data.options || [];

  const startIndex = Number(data.index || 0);
  const placeholder = String(data.placeholder || "Choose an option");
  const acceptNew = !!data.accept_new_options;
  const disabled = !!data.disabled;
  const help = data.help || "";

  // colores map (igual que en Python)
  const COLORS = {
    red: ["#e53935", "#fff"],
    orange: ["#ffb74d", "#000"],
    yellow: ["#ffd54f", "#000"],
    green: ["#43a047", "#fff"],
    blue: ["#1976d2", "#fff"],
    violet: ["#8e24aa", "#fff"],
    gray: ["#9e9e9e", "#fff"],
    grey: ["#9e9e9e", "#fff"],
    primary: ["#0f62fe", "#fff"],
    rainbow: ["linear-gradient(90deg,#ff5f6d,#ffc371)", "#fff"],
  };

  // convierte shortcodes a HTML inline
  function convertShortcodes(s) {
    if (s === null || s === undefined) return "";
    s = String(s);

    // badge :color-badge[text]
    s = s.replace(/:([a-zA-Z]+)-badge\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      const entry = COLORS[c];
      if (!entry) return `<span class="badge">${escapeHtml(text)}</span>`;
      const bg = entry[0],
        fg = entry[1];
      return `<span style="background:${bg};color:${fg};padding:2px 8px;border-radius:999px;font-size:0.8rem;display:inline-block;">${escapeHtml(
        text
      )}</span>`;
    });

    // background :color-background[text]
    s = s.replace(/:([a-zA-Z]+)-background\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      const entry = COLORS[c];
      if (!entry) return `<span class="bg-${c}">${escapeHtml(text)}</span>`;
      const bg = entry[0],
        fg = entry[1];
      return `<span style="background:${bg};color:${fg};padding:2px 6px;border-radius:6px;display:inline-block;">${escapeHtml(
        text
      )}</span>`;
    });

    // color[text]
    s = s.replace(/:([a-zA-Z]+)\[(.*?)\]/g, (m, color, text) => {
      const c = color.toLowerCase();
      const entry = COLORS[c];
      let css_color = entry ? entry[0] : c;
      if (
        typeof css_color === "string" &&
        css_color.startsWith("linear-gradient")
      ) {
        css_color = entry ? entry[1] : "#000";
      }
      return `<span style="color:${css_color}">${escapeHtml(text)}</span>`;
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
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

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
  if (!disabled) {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      list.style.display = list.style.display === "block" ? "none" : "block";
    });
    document.addEventListener("click", (e) => {
      if (!root.contains(e.target)) hideList();
    });
  }
}
