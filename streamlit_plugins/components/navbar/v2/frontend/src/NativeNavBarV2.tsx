/** @jsxImportSource react */
import React from "react";

import NavItem from "./NavItem";
import NavSubItem from "./NavSubItem";

// ===========================================================================
// Types
// ===========================================================================

export interface MenuItem {
  icon?: string;
  id: string;
  label: string;
  isDefault?: boolean;
  ttip?: string;
  submenu?: MenuItem[];
  style?: Record<string, string>;
  url?: string;
  dataset?: Record<string, string>;
}

export interface OverrideTheme {
  menu_background: string;
  txc_inactive: string;
  txc_active: string;
  option_active: string;
}

export interface ThemeData {
  name: string;
  icon: string;
  themeInfo: Record<string, unknown>;
}

export type PositionMode = "top" | "under" | "side" | "static" | "hidden";

export interface NativeNavBarV2Props {
  menu_definition: MenuItem[];
  home?: MenuItem;
  login?: MenuItem;
  override_theme?: OverrideTheme;
  position_mode: PositionMode;
  is_sticky: boolean;

  is_navigation: boolean;
  default_page_selected_id: string;
  override_page_selected_id?: string;
  override_first_page_load_id?: string;
  reclick_load?: boolean;
  prefix_url?: string;
  url_navigation?: boolean;
  key?: string;
  fvalue?: boolean;
  themes_data?: ThemeData[];
  theme_changer?: boolean;
  collapsible?: boolean;
  is_visible?: boolean;
}

// ===========================================================================
// Helpers
// ===========================================================================

function containsEmojis(input: string): boolean {
  for (const c of input) {
    const cHex = c.codePointAt(0);
    if (!cHex) continue;
    const sHex = cHex.toString(16);
    const lHex = sHex.length;
    if (lHex <= 3) continue;
    const prefix = sHex.substring(0, 2);
    if (lHex === 5 && prefix === "1f") return true;
    if (lHex === 4 && ["20","21","23","24","25","26","27","2B","29","30","32"].indexOf(prefix) > -1)
      return true;
  }
  return false;
}

function setBodyNavState(pageId: string | null, expandSubMenu: boolean, selectedSubMenu: string | null): void {
  if (pageId !== null && pageId !== undefined) {
    (document.body.dataset as any).pageId = pageId;
  } else {
    delete (document.body.dataset as any).pageId;
  }
  (document.body.dataset as any).expandSubMenu = String(expandSubMenu);
  if (selectedSubMenu !== null && selectedSubMenu !== undefined) {
    (document.body.dataset as any).selectedSubMenu = selectedSubMenu;
  } else {
    delete (document.body.dataset as any).selectedSubMenu;
  }
}

function clearBodyNavState(): void {
  delete (document.body.dataset as any).pageId;
  delete (document.body.dataset as any).expandSubMenu;
  delete (document.body.dataset as any).selectedSubMenu;
}

function toggleSidebarBody(isExpanded: boolean, positionMode: PositionMode): void {
  if (positionMode !== "side") {
    document.body.classList.remove("side-nav-open", "side-nav-closed");
    return;
  }
  if (isExpanded) {
    document.body.classList.add("side-nav-open");
    document.body.classList.remove("side-nav-closed");
  } else {
    document.body.classList.add("side-nav-closed");
    document.body.classList.remove("side-nav-open");
  }
}

function saveThemeLocal(themeData: ThemeData): void {
  try {
    localStorage.setItem("stPluginsActiveTheme-/-v1", JSON.stringify(themeData));
  } catch {
    // ignore
  }
  (document.body.dataset as any).themeName = themeData.name || "Custom";
}

function loadThemeFromLocal(): ThemeData | null {
  try {
    const raw = localStorage.getItem("stPluginsActiveTheme-/-v1");
    if (!raw) return null;
    return JSON.parse(raw) as ThemeData;
  } catch {
    return null;
  }
}

function clearThemeLocal(): void {
  try {
    localStorage.removeItem("stPluginsActiveTheme-/-v1");
  } catch {
    // ignore
  }
  delete (document.body.dataset as any).themeName;
}

function setURLPath(urlPath: string): void {
  const regexp = new RegExp("^/+|/+$", "g");
  const cleaned = urlPath.replace(regexp, "");
  const fullURL = `${window.location.origin}/${cleaned}`;
  window.history.pushState({ additionalInformation: "Updated the URL with JS" }, "", fullURL);
}

function getPageFromURL(prefixUrl: string, defaultValue: string, menuDefinition: MenuItem[]): string {
  const url = new URL(window.location.href);
  let path = url.pathname.replace(/^\/+|\/+$/g, "");
  if (prefixUrl) {
    const prefix = prefixUrl.replace(/^\/+|\/+$/g, "");
    if (path.startsWith(prefix)) {
      path = path.slice(prefix.length).replace(/^\/+/, "");
    }
  }
  if (!path) return defaultValue;

  function findItem(items: MenuItem[]): MenuItem | undefined {
    for (const item of items) {
      if (item.url === path || item.url === "/" + path) return item;
      if (item.submenu) {
        const found = findItem(item.submenu);
        if (found) return found;
      }
    }
    return undefined;
  }
  const match = findItem(menuDefinition);
  return match ? match.id : defaultValue;
}

// ===========================================================================
// Main NavBar React component (exportado como default para uso en index.tsx)
// ===========================================================================

const NativeNavBarV2: React.FC<{
  args: NativeNavBarV2Props;
  theme: {
    base: string;
    primaryColor: string;
    backgroundColor: string;
    secondaryBackgroundColor: string;
    textColor: string;
    font: string;
  } | undefined;
  setStateValue: (key: string, value: unknown) => void;
}> = ({ args, theme, setStateValue }) => {
  const {
    menu_definition,
    home,
    login,
    override_theme,
    position_mode,
    is_sticky,
    is_navigation,
    default_page_selected_id,
    override_page_selected_id,
    override_first_page_load_id,
    reclick_load = true,
    prefix_url = "",
    url_navigation = false,
    key = `${Date.now()}`,
    themes_data = [],
    theme_changer = false,
    collapsible = true,
    is_visible = true,
  } = args;

  const keyRef = React.useRef(key);
  keyRef.current = key;

  // ---------- state ----------
  const [selectedPageId, setSelectedPageId] = React.useState<string | null>(default_page_selected_id);
  const [selectedSubMenu, setSelectedSubMenu] = React.useState<string | null>(null);
  const [expandState, setExpandState] = React.useState(!collapsible);
  const [expandSubMenu, setExpandSubMenu] = React.useState(false);
  const [themeIndex, setThemeIndex] = React.useState(0);
  const [isVisible, setIsVisible] = React.useState(is_visible);

  // ---------- derived ----------

  const addHomeLogin = (): MenuItem[] => {
    const items = [...menu_definition];
    if (home) items.unshift({ ...home, icon: home.icon || ":material/home:" });
    if (login) items.push({ ...login, dataset: { login: "true" } });
    return items;
  };

  const applyNavTheme = (): React.ReactNode => {
    const mergedTheme = {
      menu_background: (theme?.backgroundColor || override_theme?.menu_background || "var(--background-color)") as string,
      txc_inactive: (theme?.textColor || override_theme?.txc_inactive || "var(--text-color)") as string,
      txc_active: (theme?.textColor || override_theme?.txc_active || "var(--text-color)") as string,
      option_active: (theme?.primaryColor || override_theme?.option_active || "var(--primary-color)") as string,
    };

    return (
      <style>
        {`
          :root {
            --menu_background: ${mergedTheme.menu_background};
            --txc_inactive: ${mergedTheme.txc_inactive};
            --txc_active: ${mergedTheme.txc_active};
            --option_active: ${mergedTheme.option_active};
            --option_active_opacity: ${mergedTheme.option_active}99;
            --option_active_translucent: ${mergedTheme.option_active}38;
          }
        `}
      </style>
    );
  };

  // ---------- effects ----------

  // Read body dataset on mount (navigation mode)
  React.useEffect(() => {
    if (!is_navigation) return;
    const bodyPageId = (document.body.dataset as any).pageId;
    const bodyExpandSub = (document.body.dataset as any).expandSubMenu === "true";
    const bodySelectedSub = (document.body.dataset as any).selectedSubMenu || null;

    if (bodyPageId && bodyPageId !== "null" && bodyPageId !== "undefined") {
      setSelectedPageId(bodyPageId);
    } else {
      const initialId = override_first_page_load_id || default_page_selected_id;
      setSelectedPageId(initialId);
    }
    setExpandSubMenu(bodyExpandSub);
    if (bodySelectedSub) setSelectedSubMenu(bodySelectedSub);
  }, [is_navigation, default_page_selected_id, override_first_page_load_id]);

  // URL navigation on mount
  React.useEffect(() => {
    if (!url_navigation) return;
    const pageId = getPageFromURL(prefix_url, default_page_selected_id, menu_definition);
    setSelectedPageId(pageId);
    setSelectedSubMenu(null);
    setExpandSubMenu(false);
    setBodyNavState(pageId, false, null);
    setIsVisible(true);
    setStateValue("selectedPageId", pageId);
  }, [url_navigation, prefix_url, default_page_selected_id, menu_definition, setStateValue]);

  // Override page selected on prop change
  React.useEffect(() => {
    if (!override_page_selected_id) return;
    const pid = override_page_selected_id;
    setSelectedPageId(pid);
    setSelectedSubMenu(null);
    setExpandSubMenu(false);
    setBodyNavState(pid, false, null);
    setIsVisible(true);
    setStateValue("selectedPageId", pid);
  }, [override_page_selected_id, default_page_selected_id, setStateValue]);

  // Theme from localStorage on mount
  React.useEffect(() => {
    if (!theme_changer || themes_data.length === 0) return;
    const saved = loadThemeFromLocal();
    if (saved) {
      const idx = themes_data.findIndex((t) => t.name === saved.name);
      const resolvedIdx = idx === -1 ? 0 : idx;
      setThemeIndex(resolvedIdx);
      saveThemeLocal(themes_data[resolvedIdx]);
    }
  }, [theme_changer, themes_data]);

  // Listen to body changes (navigation mode)
  React.useEffect(() => {
    if (!is_navigation || position_mode !== "side") return;
    const handler = () => {
      const bodyPageId = (document.body.dataset as any).pageId;
      const isSideOpen = document.body.classList.contains("side-nav-open");
      const expandSubMenu = (document.body.dataset as any).expandSubMenu === "true";
      const selectedSubMenu = (document.body.dataset as any).selectedSubMenu || null;
      if (bodyPageId && bodyPageId !== "null" && bodyPageId !== "undefined") {
        setSelectedPageId(bodyPageId);
      }
      setExpandState(isSideOpen);
      setExpandSubMenu(expandSubMenu);
      if (selectedSubMenu) setSelectedSubMenu(selectedSubMenu);
    };
    document.body.addEventListener("click", handler);
    return () => document.body.removeEventListener("click", handler);
  }, [is_navigation, position_mode]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      clearBodyNavState();
      clearThemeLocal();
    };
  }, [key]);

  // ---------- actions ----------

  const clickOnPage = (item: MenuItem) => {
    const prevId = selectedPageId;
    const itemId = item.id;
    setSelectedPageId(itemId);
    setExpandState(false);
    setExpandSubMenu(false);
    setSelectedSubMenu(null);

    if (prevId !== itemId || reclick_load) {
      setStateValue("selectedPageId", itemId);
      setBodyNavState(itemId, false, null);
      setURLPath(item.url || "");
    }
  };

  const toggleSubMenu = (parentId: string) => {
    let newSelectedSubMenu = selectedSubMenu;
    let newExpandSubMenu = expandSubMenu;
    if (selectedSubMenu === parentId) {
      newExpandSubMenu = !expandSubMenu;
    } else {
      newExpandSubMenu = true;
      newSelectedSubMenu = parentId;
    }
    if (!newExpandSubMenu) newSelectedSubMenu = null;

    setSelectedSubMenu(newSelectedSubMenu);
    setExpandSubMenu(newExpandSubMenu);
    setBodyNavState(selectedPageId, newExpandSubMenu, newSelectedSubMenu);
  };

  const toggleNav = () => {
    const newExpand = !expandState;
    setExpandState(newExpand);
    if (position_mode !== "side") setExpandSubMenu(false);
    toggleSidebarBody(newExpand, position_mode);
  };

  const themeToggle = () => {
    const nextIdx = (themeIndex + 1) % themes_data.length;
    setThemeIndex(nextIdx);
    saveThemeLocal(themes_data[nextIdx]);
  };

  // ---------- render ----------

  if (!isVisible) return null;

  const menuItems = addHomeLogin();
  const currentTheme = themes_data[themeIndex];
  const themeIcon = currentTheme?.icon || "format_paint";
  const themeTooltip = currentTheme?.name || "Toggle theme";
  const navbarId = `navbar-${key}`;

  return (
    <div key={key}>
      {applyNavTheme()}
      <nav
        id={navbarId}
        className={`navbar navbar-expand-custom navbar-mainbg py-0 py-md-0 ${position_mode}`}
      >
        <button
          className="navbar-toggler"
          type="button"
          onClick={toggleNav}
          aria-expanded={expandState}
        >
          <span className="material-symbols-rounded text-color menu-closed">menu</span>
          <span className="material-symbols-rounded text-color menu-open">menu_open</span>
        </button>
        <div className={`navbar-collapse navbar-wrapper ${expandState ? "nav-open" : "nav-close"}`}>
          <ul className="navbar-nav py-0">
            {menuItems.map((item: MenuItem, index: number) => {
              const isActive = item.id === selectedPageId;
              const icon = item.icon;
              let iconContent = "";
              if (position_mode === "side") {
                iconContent = item.label.charAt(0).toUpperCase();
              }
              let iconMarkup: React.ReactNode = <span className="icon icon-placeholder">{iconContent}</span>;

              if (icon) {
                const regex = /:material\/(\w+):/gm;
                const m = regex.exec(icon);
                if (m !== null) {
                  iconMarkup = <span className="material-symbols-rounded icon">{m[1]}</span>;
                } else {
                  const iconClass = containsEmojis(icon) ? "icon" : `${icon} icon`;
                  const iconTxt = containsEmojis(icon) ? icon : "";
                  iconMarkup = <i className={iconClass}>{iconTxt}</i>;
                }
              }

              const dataAttributes = item.dataset
                ? Object.entries(item.dataset).reduce(
                    (acc, [k, v]) => {
                      (acc as any)[`data-${k}`] = v;
                      return acc;
                    },
                    {} as Record<string, unknown>
                  )
                : {};

              if (item.submenu) {
                return (
                  <li
                    style={item.style as React.CSSProperties}
                    className={`nav-item py-0 dropdown ${isActive ? "active" : ""}`}
                    key={index * 100}
                    {...dataAttributes}
                  >
                    <a
                      className="nav-link dropdown-toggle"
                      href={"#_sub" + index}
                      onClick={() => toggleSubMenu(item.id)}
                      data-toggle="tooltip"
                      data-placement="top"
                      data-html="true"
                      title={item.ttip}
                    >
                      {iconMarkup}
                      <span>{item.label}</span>
                    </a>
                    <ul
                      className={`dropdown-menu ${selectedSubMenu === item.id && expandSubMenu ? "show" : ""}`}
                    >
                      {item.submenu.map((subitem: MenuItem, subindex: number) => (
                        <NavSubItem
                          key={subindex}
                          subitem={subitem}
                          menu_id={subindex}
                          parent_id={item.id}
                          is_active={subitem.id === selectedPageId}
                          submenu_toggle={toggleSubMenu}
                          click_on_app={clickOnPage}
                        />
                      ))}
                    </ul>
                  </li>
                );
              } else {
                return (
                  <NavItem
                    key={index * 104}
                    menuitem={item}
                    menu_id={index}
                    position_mode={position_mode}
                    is_active={isActive}
                    submenu_toggle={toggleSubMenu}
                    click_on_app={clickOnPage}
                    {...dataAttributes}
                  />
                );
              }
            })}
          </ul>
        </div>
        {themes_data.length > 0 && (
          <button
            className="theme-toggler"
            type="button"
            onClick={themeToggle}
            title={themeTooltip}
          >
            <span className="material-symbols-rounded text-color">{themeIcon}</span>
          </button>
        )}
      </nav>
    </div>
  );
};

export default NativeNavBarV2;
