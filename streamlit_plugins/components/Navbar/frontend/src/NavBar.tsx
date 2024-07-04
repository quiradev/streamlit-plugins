import { Streamlit, Theme, RenderData } from "streamlit-component-lib";
import React, { ReactNode, useState, useEffect, useCallback } from "react";
import { useRenderData } from "./NavBarProvider";
import NavItem from "./NavItem.jsx";
import NavSubItem from "./NavSubItem.jsx";
import "./bootstrap.min.css";
import "./custom.css";

interface MenuItem {
  icon: string;
  id: string;
  label: string;
  ttip?: string;
  submenu?: MenuItem[];
  style?: React.CSSProperties;
}

interface OverrideTheme {
  menu_background: string;
  txc_inactive: string;
  txc_active: string;
  option_active: string;
}

interface PythonArgs {
  menu_definition: MenuItem[];
  home: MenuItem;
  login: MenuItem;
  use_animation: boolean;
  override_theme: OverrideTheme;
  default_app_selected_id: string;
  override_app_selected_id?: string;
  key?: string;
  fvalue?: boolean;
}

interface NavBarRenderData extends RenderData {
  args: PythonArgs;
  disabled: boolean;
  theme?: Theme;
}

const NavBar: React.VFC = () => {
  const renderData = useRenderData<NavBarRenderData>();

  const args: PythonArgs = renderData.args;
  // if (_app_selected_id === "") _app_selected_id = args.default_app_selected_id;

  const [expandState, setExpandState] = useState(false);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [selectedSubMenu, setSelectedSubMenu] = useState<string | null>(null);
  const [expandSubMenu, setExpandSubMenu] = useState(false);
  const [blockState, setBlockState] = useState("none");

  // Handle override_app_selected_id updates
  useEffect(() => {
    if (args.override_app_selected_id) {
      console.log(args.override_app_selected_id);
      setSelectedAppId(args.override_app_selected_id);
      setExpandState(false);
      setBlockState("none");
      setExpandSubMenu(false);
      Streamlit.setComponentValue(args.override_app_selected_id);
    }
  }, [args.override_app_selected_id]);

  const handleResize = useCallback(() => {
    let lastHeight = document.body.scrollHeight;
    const step_resize = () => {
      Streamlit.setFrameHeight();
      if (lastHeight !== document.body.scrollHeight)
        requestAnimationFrame(step_resize);
    };
    Streamlit.setFrameHeight();
    requestAnimationFrame(step_resize);
  }, []);

  useEffect(() => {
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [handleResize]);

  // Improved loseFocus function to detect clicks outside the iframe
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!document.hasFocus()) {
        setExpandState(false);
        setBlockState("none");
        setExpandSubMenu(false);
        delayed_resize(50);
      }
    };

    const handleBlur = () => {
      setExpandState(false);
      setBlockState("none");
      setExpandSubMenu(false);

      delayed_resize(50);
    };

    window.addEventListener("blur", handleBlur);
    document.addEventListener("click", handleClickOutside);

    return () => {
      window.removeEventListener("blur", handleBlur);
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  if (!renderData) {
    return <div style={{ color: "red" }}>No hay renderData definida.</div>;
  }

  // Streamlit sends us a theme object via renderData that we can use to ensure
  // that our component has visuals that match the active theme in a
  // streamlit app.
  const { theme } = renderData;

  // Maintain compatibility with older versions of Streamlit that don't send
  // a theme object.
  if (!theme) {
    return (
      <div style={{ color: "red" }}>
        Theme is undefined, please check streamlit version.
      </div>
    );
  }

  // setMenuDefinition(renderData.args.menu_definition);
//   let _app_selected_id: string = selected_app_id;
  // let menu_definition: MenuItem[] = args.menu_definition;
//   let override_app_selected_id: string = args.override_app_selected_id || null;
//   if (override_app_selected_id) {
//     if (override_app_selected_id !== _app_selected_id) {
// //       setSelectedAppId(override_app_selected_id);
//       _app_selected_id = override_app_selected_id;
//     }
//   }

  /* Functions definition */
  const delayed_resize = (wait_time: number): NodeJS.Timeout =>
    setTimeout(() => {
      Streamlit.setFrameHeight();
    }, wait_time);

//   const framed_resize = (): void => {
//     let lastHeight = document.body.scrollHeight;
//     const step_resize = () => {
//       Streamlit.setFrameHeight();
//       if (lastHeight !== document.body.scrollHeight)
//         requestAnimationFrame(step_resize);
//     };
//     Streamlit.setFrameHeight();
//     requestAnimationFrame(step_resize);
//   };

   const containsEmojis = (input: string): boolean => {
    if (input) {
      for (const c of input) {
        const cHex = c.codePointAt(0);
        if (cHex) {
          const sHex = cHex.toString(16);
          const lHex = sHex.length;
          if (lHex > 3) {
            const prefix = sHex.substring(0, 2);

            if (lHex === 5 && prefix === "1f") {
              return true;
            }

            if (lHex === 4) {
              return (
                ["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].indexOf(prefix) > -1
              );
            }
          }
        }
      }
    }
    return false;
  };

  const addHomeLogin = (): MenuItem[] => {
    const menuItems = [...args.menu_definition];
    if (args.home) {
      menuItems.unshift(args.home);
    }
    if (args.login) {
      menuItems.push({ ...args.login, style: { marginLeft: "auto" } });
    }
    return menuItems;
  };

  const clickOnApp = (itemId: string): void => {
    setSelectedAppId(itemId);
    setExpandState(false);
    setBlockState("none");
    setExpandSubMenu(false);
    handleResize();
    Streamlit.setComponentValue(itemId);
  };

  const toggleSubMenu = (parentId: string): void => {
    if (selectedSubMenu === parentId) {
      setExpandSubMenu(!expandSubMenu);
    } else {
      setExpandSubMenu(true);
      setSelectedSubMenu(parentId);
    }
    handleResize();
  };

  const createSubMenu = (item: MenuItem, key: number): JSX.Element => (
    <NavSubItem
      subitem={item}
      menu_id={key}
      submenu_toggle={toggleSubMenu}
      click_on_app={clickOnApp}
      parent_id={item.id}
      key={key}
      is_active={item.id === selectedAppId}
    />
  );

  const toggleNav = (): void => {
    setExpandState(!expandState);
    setBlockState(expandState ? "none" : "block");
    setExpandSubMenu(false);
    handleResize();
  };

  const createMenu = (item: MenuItem, key: number): JSX.Element => {
    const isActive = item.id === selectedAppId;
    const iconClass = containsEmojis(item.icon) ? "" : item.icon;
    const iconTxt = containsEmojis(item.icon) ? item.icon : "";
//     if (!selected_app_id) {
//       if (key === first_select) {
//         // isActive = true;
//         setSelectedAppId(item.id);
//       }
//     }
//     if (item.id === override_app_selected_id && selected_app_id !== override_app_selected_id) {
//       // isActive = true;
//       setSelectedAppId(override_app_selected_id);
//       override_app_selected_id = "";
//     }
    // if (Array.isArray(item.submenu)) {
    if (item.submenu) {
      return (
        <li
          style={item.style}
          className={`nav-item py-0 dropdown ${isActive ? "active" : ""}`}
          key={key * 100}
        >
          <a
            className="nav-link dropdown-toggle"
            href={"#_sub" + key}
            key={"sub1_" + key}
            onClick={() => toggleSubMenu(item.id)}
            data-toggle="tooltip"
            data-placement="top"
            data-html="true"
            title={item.ttip}
          >
            <i className={iconClass}>{iconTxt}</i>
            <span>{item.label}</span>
          </a>
          <ul key={key * 103} className={`dropdown-menu ${selectedSubMenu === item.id && expandSubMenu ? "show" : ""}`}>
            {item.submenu.map((subitem: MenuItem, subindex: number) => createSubMenu(subitem, subindex))}
          </ul>
        </li>
      );
    } else {
      return (
        <NavItem
          menuitem={item}
          menu_id={key}
          is_active={isActive}
          submenu_toggle={toggleSubMenu}
          click_on_app={clickOnApp}
          key={key * 104}
        />
      );
    }
  };

  const applyTheme = (): ReactNode => {
    const mergedTheme = {
      menu_background: theme.backgroundColor || "#F0F2F6",
      txc_inactive: theme.textColor || "#FFFFFF",
      txc_active: theme.textColor || "#FFFFFF",
      option_active: theme.primaryColor || "#F63366"
    };

    const overrideTheme = args.override_theme;
    if (overrideTheme) {
      mergedTheme.menu_background = overrideTheme.menu_background || mergedTheme.menu_background;
      mergedTheme.txc_inactive = overrideTheme.txc_inactive || mergedTheme.txc_inactive;
      mergedTheme.txc_active = overrideTheme.txc_active || mergedTheme.txc_active;
      mergedTheme.option_active = overrideTheme.option_active || mergedTheme.option_active;
    }

    return (
      <style>
        {`
          :root {
            --menu_background: ${mergedTheme.menu_background};
            --txc_inactive: ${mergedTheme.txc_inactive};
            --txc_active: ${mergedTheme.txc_active};
            --option_active: ${mergedTheme.option_active};
            --option_active_opacity: ${theme.primaryColor}99;
            --option_active_translucent: ${theme.primaryColor}66;
          }
        `}
      </style>
    );
  };

  const renderNavBar = (): ReactNode => {
    const menuItems = addHomeLogin();
    const menuLook = args.use_animation ? "complexnavbarSupportedContent" : "navbarSupportedContent";
    const selector = args.use_animation ? (
      <div className="hori-selector">
        <div className="left"></div>
        <div className="right"></div>
      </div>
    ) : null;

    return (
      <div key={args.key}>
        {applyTheme()}
        <nav className="navbar navbar-expand-custom navbar-mainbg w-100 py-0 py-md-0">
          <button
            className="navbar-toggler"
            type="button"
            onClick={toggleNav}
            aria-expanded={expandState}
          >
            <i className="fas fa-bars text-color"></i>
          </button>
          <div id={menuLook} className="navbar-collapse" style={{ display: blockState }}>
            <ul className="navbar-nav py-0">
              {selector}
              {menuItems.map((item: MenuItem, index: number) => createMenu(item, index))}
            </ul>
          </div>
        </nav>
      </div>
    );
  };

//
//   if (!document.defineListeners) document.defineListeners = false;
//   if (!document.clickInside) document.clickInside = false;
//   const loseFocus = (): void => {
//     if (!document.defineListeners) {
//       document.defineListeners = true
//       document.addEventListener('focusout', event => {
//         setTimeout(
//         () => {
//             if (!document.clickInside) {
//               console.log("FOCUSOUT FIRE");
//               setExpandState(false);
//               setBlockState("none");
//               setExpandSubMenu(false);
//               // framed_resize();
//               delayed_resize(50);
//             }
//             document.clickInside = false;
//         }, 50
//         )
//       });
//       document.addEventListener('click', event => {
//         document.clickInside = true;
//       });
//     }
//   }
//   loseFocus();
  return renderNavBar();
};

//export default withStreamlitConnection(NavBar);
export default NavBar;
