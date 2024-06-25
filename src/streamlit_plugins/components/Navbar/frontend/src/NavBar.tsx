import { Streamlit, Theme, RenderData } from "streamlit-component-lib";
import React, { ReactNode, useState } from "react";
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
  submenu?: [];
  style?: {};
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
  use_animation: boolean;
  login: MenuItem;
  first_select: number;
  override_theme: OverrideTheme;
  override_app_selected_id: string;
  key?: string;
  fvalue?: boolean;
}

interface NavBarRenderData extends RenderData {
  args: PythonArgs;
  disabled: boolean;
  theme?: Theme;
}

const NavBar: React.VFC = () => {
  const renderData: NavBarRenderData | undefined = useRenderData();

  const [expand_state, setExpandState] = useState(false);
  const [selected_app_id, setSelectedAppId] = useState<null | string>(null);
  const [selected_submenu, setSelectedSubMenu] = useState<null | string>(null);
  const [expand_submenu, setExpandSubmenu] = useState(false);
  const [block_state, setBlockState] = useState("none");

  if (renderData == null) {
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

  const args: PythonArgs = renderData.args;
  let menu_definition: MenuItem[] = args.menu_definition;
  let override_app_selected_id: string = args.override_app_selected_id || "";

  /* Functions definition */
  const delayed_resize = (wait_time: number): NodeJS.Timeout =>
    setTimeout(() => {
      Streamlit.setFrameHeight();
    }, wait_time);

  const framed_resize = (): void => {
    let lastHeight = document.body.scrollHeight;
    const step_resize = () => {
      Streamlit.setFrameHeight();
      if (lastHeight !== document.body.scrollHeight)
        requestAnimationFrame(step_resize);
    };
    Streamlit.setFrameHeight();
    requestAnimationFrame(step_resize);
  };

  const containsEmojis = (input: string): boolean => {
    if (input) {
      for (var c of input) {
        var cHex = ("" + c).codePointAt(0);
        if (cHex) {
          var sHex = cHex.toString(16);
          var lHex = sHex.length;
          if (lHex > 3) {
            var prefix = sHex.substring(0, 2);

            if (lHex === 5 && prefix === "1f") {
              return true;
            }

            if (lHex === 4) {
              return (
                [
                  "20",
                  "21",
                  "23",
                  "24",
                  "25",
                  "26",
                  "27",
                  "2B",
                  "29",
                  "30",
                  "32"
                ].indexOf(prefix) > -1
              );
            }
          }
        }
      }
    }

    return false;
  };

  const addHomeLogin = (): void => {
    let home = args.home;

    if (home) {
      menu_definition = [
        { id: home.id, label: home.label, icon: home.icon, ttip: home.ttip },
        ...menu_definition
      ];
    }

    let using_secure = args.login;
    if (using_secure) {
      menu_definition = [
        ...menu_definition,
        {
          id: using_secure.id,
          label: using_secure.label,
          icon: using_secure.icon,
          ttip: using_secure.ttip,
          style: { marginLeft: "auto" }
        }
      ];
    }
  };

  const clickOnApp = (item_id: string, subitem_id?: string): void => {
    let id: string = subitem_id || item_id;
    setSelectedAppId(id);
    setExpandState(false);
    setBlockState("none");
    setExpandSubmenu(false);
    framed_resize();
    Streamlit.setComponentValue(id);
  };

  const toggleSubMenu = (parent_id: string): void => {
    if (parent_id === "") {
      setExpandSubmenu(false);
    } else {
      if (selected_submenu === parent_id) setExpandSubmenu(!expand_submenu);
      else setExpandSubmenu(true);
      setSelectedSubMenu(parent_id);
    }

    // delayed_resize(250);
    framed_resize();
  };

  const create_submenu = (item: MenuItem, kid: number): JSX.Element => {
    return (
      <NavSubItem
        subitem={item}
        menu_id={kid}
        submenu_toggle={toggleSubMenu}
        click_on_app={clickOnApp}
        parent_id={item.id}
        key={kid}
        is_active={item.id === selected_app_id}
      />
    );
  };

  const toggleNav = (): void => {
    if (expand_state) {
      setExpandState(false);
      setBlockState("none");
      setExpandSubmenu(false);
    } else {
      setExpandState(true);
      setBlockState("block");
    }
    framed_resize();
  };

  const create_menu = (
    item: MenuItem,
    kid: number,
    issub: boolean
  ): JSX.Element => {
    let first_select = args.first_select;
    let label = "";
    let iconClass = "";
    let iconTxt = "";

    if (containsEmojis(item.icon)) {
      iconTxt = item.icon;
      label = item.label;
    } else {
      iconClass = item.icon;
      label = item.label;
    }
    let isActive: boolean = false;
    if (!selected_app_id) {
      if (kid === first_select) {
        // isActive = true;
        setSelectedAppId(item.id);
      }
    }
    if (item.id === override_app_selected_id && selected_app_id !== override_app_selected_id) {
      // isActive = true;
      setSelectedAppId(override_app_selected_id);
    }

    if (selected_app_id === item.id) {
      isActive = true;
      Streamlit.setComponentValue(selected_app_id);
    }
    if (Array.isArray(item.submenu)) {
      return (
        <li
          style={item.style || {}}
          className={`nav-item py-0 dropdown ${isActive ? "active" : ""}`}
          key={kid * 100}
        >
          <a
            className="nav-link dropdown-toggle"
            href={"#_sub" + kid}
            key={"sub1_" + kid}
            onClick={() => toggleSubMenu(item.id)}
            data-toggle="tooltip"
            data-placement="top"
            data-html="true"
            title={item.ttip}
          >
            <i className={iconClass}>{iconTxt}</i>
            <span>{label}</span>
          </a>
          <ul
            className={
              selected_submenu === item.id && expand_submenu
                ? "dropdown-menu show"
                : "dropdown-menu"
            }
            key={kid * 103}
          >
            {item.submenu.map((item: MenuItem, index: number) =>
              create_submenu(item, index)
            )}
          </ul>
        </li>
      );
    } else {
      return (
        <NavItem
          menuitem={item}
          menu_id={kid}
          is_active={isActive}
          submenu_toggle={toggleSubMenu}
          click_on_app={clickOnApp}
        />
      );
    }
  };

  const setTheme = (): ReactNode => {
    let merged_theme = {
      menu_background: "#F0F2F6",
      txc_inactive: "#FFFFFF",
      txc_active: "#FFFFFF",
      option_active: "#F63366"
    };

    if (theme) {
      merged_theme.menu_background = theme.backgroundColor;
      merged_theme.txc_inactive = theme.textColor;
      merged_theme.txc_active = theme.textColor;
      merged_theme.option_active = theme.primaryColor;
    }
    let override_theme = args.override_theme;
    if (override_theme) {
      merged_theme.menu_background =
        override_theme.menu_background ?? merged_theme.menu_background;
      merged_theme.txc_inactive =
        override_theme.txc_inactive ?? merged_theme.txc_inactive;
      merged_theme.txc_active =
        override_theme.txc_active ?? merged_theme.txc_active;
      merged_theme.option_active =
        override_theme.option_active ?? merged_theme.option_active;
    }

    return (
      <style>
        {`
          :root {
            --menu_background: ${merged_theme.menu_background};
            --txc_inactive: ${merged_theme.txc_inactive};
            --txc_active: ${merged_theme.txc_active};
            --option_active: ${merged_theme.option_active};
            --option_active_opacity: ${theme.primaryColor}99;
            --option_active_translucent: ${theme.primaryColor}66;
          }
        `}
      </style>
    );
  };

  const complex_nav = (): ReactNode => {
    let menu_look = "complexnavbarSupportedContent";
    let selector = (
      <div className="hori-selector">
        <div className="left"></div>
        <div className="right"></div>
      </div>
    );

    if (args.use_animation) {
      menu_look = "complexnavbarSupportedContent";
      selector = (
        <div className="hori-selector">
          <div className="left"></div>
          <div className="right"></div>
        </div>
      );
    } else {
      menu_look = "navbarSupportedContent";
      selector = <></>;
    }
    return (
      <div key={args.key}>
        {setTheme()}
        <nav className="navbar navbar-expand-custom navbar-mainbg w-100 py-0 py-md-0">
          <button
            className="navbar-toggler"
            type="button"
            onClick={() => toggleNav()}
            aria-expanded={expand_state}
          >
            <i className="fas fa-bars text-color"></i>
          </button>
          <div
            className="navbar-collapse"
            id={menu_look}
            style={{ display: block_state }}
          >
            <ul className="navbar-nav py-0">
              {selector}
              {addHomeLogin()}
              {menu_definition.map((item: MenuItem, index: number) =>
                create_menu(item, index, false)
              )}
            </ul>
          </div>
        </nav>
      </div>
    );
  };
  if (!document.defineListeners) document.defineListeners = false;
  if (!document.clickInside) document.clickInside = false;
  const loseFocus = (): void => {
    if (!document.defineListeners) {
      document.defineListeners = true
      document.addEventListener('focusout', event => {
        setTimeout(
        () => {
            if (!document.clickInside) {
              console.log("FOCUSOUT FIRE");
              setExpandState(false);
              setBlockState("none");
              setExpandSubmenu(false);
            // framed_resize();
              delayed_resize(50);
            }
            document.clickInside = false;
        }, 50
        )
      });
      document.addEventListener('click', event => {
        document.clickInside = true;
      });
    }
  }
  loseFocus();
  return complex_nav();
};

//export default withStreamlitConnection(NavBar);
export default NavBar;
