import React, { ReactNode } from "react";

import { Streamlit, Theme, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import { BaseProvider, LightTheme } from "baseui"

import { Client as Styletron } from "styletron-engine-atomic"
import { Provider as StyletronProvider } from "styletron-react"

import { createPopper } from '@popperjs/core';

// import { useRenderData } from "./NavBarProvider";
import NavItem from "./NavItem.jsx";
import NavSubItem from "./NavSubItem.jsx";

// Initialize our Styletron engine
const engine = new Styletron()

interface MenuItem {
  icon: string;
  id: string;
  label: string;
  ttip?: string;
  submenu?: MenuItem[];
  style?: React.CSSProperties;
  dataset?: object;
}

interface OverrideTheme {
  menu_background: string;
  txc_inactive: string;
  txc_active: string;
  option_active: string;
}

type PositionMode = "top" | "under" | "side";

interface PythonArgs {
  menu_definition: MenuItem[];
  home: MenuItem;
  login: MenuItem;
  use_animation: boolean;
  override_theme: OverrideTheme;
  position_mode: PositionMode;
  default_app_selected_id: string;
  override_app_selected_id?: string;
  reclick_load?: boolean;
  key?: string;
  fvalue?: boolean;
}

// interface NavBarRenderData extends RenderData {
//   args: PythonArgs;
//   disabled: boolean;
//   theme?: Theme;
// }

interface State {
  selectedAppId: string;
  expandState: boolean;
  selectedSubMenu: string | null;
  expandSubMenu: boolean;
  blockState: string;
  fromClick: boolean;
}

class StreamlitComponentBase<S = {}> extends React.PureComponent<
  ComponentProps,
  S
> {
  public componentDidMount(): void {
    // After we're rendered for the first time, tell Streamlit that our height has changed.
    Streamlit.setFrameHeight();
  }

  public componentDidUpdate(prevProps: ComponentProps, prevState: Readonly<S>, snapshot?: any): void {
    // After we're updated, tell Streamlit that our height may have changed.
    Streamlit.setFrameHeight();
  }
}

class NativeNavBar extends StreamlitComponentBase<State> {
    theme: Theme;
    maxNavBarWidth: number = 0;
    resizeTimeout: NodeJS.Timeout | null = null;

    public constructor(props: ComponentProps) {
        super(props);
        const args: PythonArgs = props.args;

        let selectedAppId = args.default_app_selected_id;
        let expandState = false;
        let selectedSubMenu = null;
        let blockState = "none";
        let expandSubMenu = false;

        if (args.override_app_selected_id) {
            selectedAppId = args.override_app_selected_id;
            Streamlit.setComponentValue(selectedAppId);
        }

        // console.log("SELECCIONADA", selectedAppId, args.override_app_selected_id, args.default_app_selected_id);

        this.state = {
            selectedAppId: selectedAppId,
            selectedSubMenu: selectedSubMenu,
            expandState: expandState,
            expandSubMenu: expandSubMenu,
            blockState: blockState,
            fromClick: false
        };


        // if (!renderData) {
        //   return <div style={{ color: "red" }}>No hay renderData definida.</div>;
        // }

        // Streamlit sends us a theme object via renderData that we can use to ensure
        // that our component has visuals that match the active theme in a
        // streamlit app.
        let theme: Theme | undefined = this.props.theme;

        // Maintain compatibility with older versions of Streamlit that don't send
        // a theme object.
        if (!theme) {
            // return (
            //     <div style={{ color: "red" }}>
            //     Theme is undefined, please check streamlit version.
            //     </div>
            // );
            theme = {
                base: "light",
                backgroundColor: "#FFFFFF",
                textColor: "#31333F",
                primaryColor: "#FF4B4B",
                secondaryBackgroundColor: "#F0F2F6",
                font: "Sans serif"
            }
        }
        this.theme = theme;
    }

    public componentDidMount = () => {
        // console.log(
        //     "DidMount",
        //     this.state.selectedAppId, this.props.args.override_app_selected_id, this.props.args.default_app_selected_id,
        //     this.state.fromClick
        // );

        // useEffect resize
        // this.handleResize();
        this.calculateMaxNavBarWidth();
        window.addEventListener("resize", this.handleResize);

        // useEffect functions to detect clicks outside the iframe
        window.addEventListener("blur", this.handleBlur);
        document.addEventListener("click", this.handleClickOutside);

        Streamlit.setFrameHeight();
    }

    public componentDidUpdate = (prevProps: ComponentProps, prevState: State, snapshot?: any): void => {
        // Han cambiado los argumentos de PythonArgs sin hacer el DidMount
        // Si se llama desde python programaticamente
        const args: PythonArgs = this.props.args

        let selectedAppId = this.state.selectedAppId;
        // let prevSelectedAppId = prevState.selectedAppId;

        let argDefault = args.default_app_selected_id;
        let prevArgDefault = prevProps.args.default_app_selected_id;
        let argOverride = args.override_app_selected_id;
        let prevArgOverride = prevProps.args.override_app_selected_id;

        // console.log(
        //     "DidUpdate",
        //     this.state.selectedAppId, this.props.args.override_app_selected_id, this.props.args.default_app_selected_id,
        //     this.state.fromClick
        // );

        if (prevArgDefault !== argDefault || prevArgOverride !== argOverride) {

            selectedAppId = this.state.selectedAppId;

            // console.log(
            //     "Props DidUpdate",
            //     this.state.selectedAppId, this.props.args.override_app_selected_id, this.props.args.default_app_selected_id,
            //     this.state.fromClick
            // );
            if (argOverride) {
                selectedAppId = argOverride || argDefault;

                this.setState(
                    {
                        selectedAppId: selectedAppId,
                        selectedSubMenu: this.state.selectedSubMenu,
                        expandState: this.state.expandState,
                        expandSubMenu: this.state.expandSubMenu,
                        blockState: this.state.blockState,
                        fromClick: false
                    },
                    () => {
                        this.handleResize();
                        if (prevArgOverride !== argOverride) Streamlit.setComponentValue(selectedAppId);
                    }
                );
            }
        }
    }

    public componentWillUnmount = () => {
        // console.log("Unmount", this.state.selectedAppId);

        // useEffect resize
        window.removeEventListener("resize", this.handleResize);

        // useEffect functions to detect clicks outside the iframe
        window.removeEventListener("blur", this.handleBlur);
        document.removeEventListener("click", this.handleClickOutside);

        Streamlit.setFrameHeight();
    }

    /* Functions definition */
    private calculateMaxNavBarWidth = () => {
        const navbar$ = document.querySelector('nav.navbar') as HTMLElement;
        if (navbar$ === null) return;

        const container$ = navbar$.querySelector("#complexnavbarSupportedContent") as HTMLElement;
        if (container$ === null) return;

        const listItems$ = container$.querySelectorAll(":scope > ul > li") as NodeListOf<HTMLElement>;
        if (listItems$.length === 0) return;

        container$.style.display = "block";

        let totalWidth = 0;
        listItems$.forEach((li) => {
            totalWidth += li.clientWidth;
        });

        this.maxNavBarWidth = totalWidth;
    }
    private checkNavbarOverflow = () => {
        const navbar$ = document.querySelector('nav.navbar') as HTMLElement;
        if (navbar$ === null) return;

        let navBarWidth = navbar$.clientWidth;

        if (navBarWidth < this.maxNavBarWidth) {
            navbar$.classList.add('collapsed');
        } else {
            navbar$.classList.remove('collapsed');
        }
    };

    private handleClickOutside = (event: MouseEvent) => {
        if (!document.hasFocus()) {
            this.setState(
                {
                    selectedAppId: this.state.selectedAppId,
                    selectedSubMenu: this.state.selectedSubMenu,
                    expandState: false,
                    expandSubMenu: false,
                    blockState: "none",
                    fromClick: false
                },
                () => this.delayed_resize(50)
            );
        }
    };

    private handleBlur = () => {
        this.setState(
            {
                selectedAppId: this.state.selectedAppId,
                selectedSubMenu: this.state.selectedSubMenu,
                expandState: false,
                expandSubMenu: false,
                blockState: "none",
                fromClick: false
            },
            () => this.delayed_resize(50)
        );
    };

    private handleResize = () => {
        if (this.resizeTimeout) {
            clearTimeout(this.resizeTimeout);
        }
        this.resizeTimeout = setTimeout(() => {
            this.checkNavbarOverflow();
        }, 200);

        Streamlit.setFrameHeight();
    };

    private delayed_resize = (wait_time: number): NodeJS.Timeout => {
        return setTimeout(() => {
            Streamlit.setFrameHeight();
        }, wait_time);
    };

    private containsEmojis = (input: string): boolean => {
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

    private addHomeLogin = (): MenuItem[] => {
        const args: PythonArgs = this.props.args;
        const menuItems = [...args.menu_definition];
        if (args.home) {
            menuItems.unshift(args.home);
        }
        if (args.login) {
            menuItems.push({ ...args.login, style: { marginLeft: "auto" }, dataset: { login: true } });
        }
        return menuItems;
    };

    private clickOnApp = (itemId: string): void => {
        let prevSelectedAppId = this.state.selectedAppId;
        this.setState(
            {
                selectedAppId: itemId,
                selectedSubMenu: null,
                expandState: false,
                expandSubMenu: false,
                blockState: "none",
                fromClick: true
            },
            () => {
                this.handleResize();
                if (prevSelectedAppId !== itemId || this.props.args.reclick_load) Streamlit.setComponentValue(itemId);
            }
        );
    };

    private toggleSubMenu = (parentId: string): void => {
        let selectedSubMenu = this.state.selectedSubMenu;
        let expandSubMenu = this.state.expandSubMenu;
        if (this.state.selectedSubMenu === parentId) {
            expandSubMenu = !expandSubMenu;
        } else {
            expandSubMenu = true;
            selectedSubMenu = parentId;
        }
        this.setState(
            {
                selectedAppId: this.state.selectedAppId,
                selectedSubMenu: selectedSubMenu,
                expandState: this.state.expandState,
                expandSubMenu: expandSubMenu,
                blockState: this.state.blockState,
                fromClick: false
            },
            () => this.handleResize()
        );

    };

    private createSubMenu = (item: MenuItem, key: number): JSX.Element => (
        <NavSubItem
        subitem={item}
        menu_id={key}
        submenu_toggle={this.toggleSubMenu}
        click_on_app={this.clickOnApp}
        parent_id={item.id}
        key={key}
        is_active={item.id === this.state.selectedAppId}
        />
    );

    private toggleNav = (): void => {
        this.setState(
            {
                selectedAppId: this.state.selectedAppId,
                selectedSubMenu: this.state.selectedSubMenu,
                expandState: !this.state.expandState,
                expandSubMenu: false,
                blockState: this.state.expandState ? "none" : "block",
                fromClick: false
            },
            () => this.handleResize()
        );
    };

    private createMenu = (item: MenuItem, key: number): JSX.Element => {
        const isActive = item.id === this.state.selectedAppId;
        const hasIcon = item.icon ? true : false;

        let iconMarkup;

        // Determinar si se usa <i> o <span> para el icono
        if (hasIcon) {
            const regex = /:material\/(\w+):/gm;
            const m = regex.exec(item.icon);
            if (m !== null) {
                const symbol = m[1];
                iconMarkup = <span className="material-symbols-rounded icon">{symbol}</span>;
            }
            else {
                const iconClass = this.containsEmojis(item.icon) ? "icon" : `${item.icon} icon`;
                const iconTxt = this.containsEmojis(item.icon) ? item.icon : "";
                iconMarkup = <i className={iconClass}>{iconTxt}</i>;
            }
        }
        // Construir los atributos data-* a partir de item.dataset
        const dataAttributes = item.dataset ? Object.entries(item.dataset).reduce((acc, [key, value]) => {
            acc[`data-${key}`] = value;
            return acc;
        }, {} as { [key: string]: any }) : {};

        if (item.submenu) {
            return (
                <li
                    style={item.style}
                    className={`nav-item py-0 dropdown ${isActive ? "active" : ""}`}
                    key={key * 100}
                    {...dataAttributes}
                >
                <a
                    className="nav-link dropdown-toggle"
                    href={"#_sub" + key}
                    key={"sub1_" + key}
                    onClick={() => this.toggleSubMenu(item.id)}
                    data-toggle="tooltip"
                    data-placement="top"
                    data-html="true"
                    title={item.ttip}
                >
                    {hasIcon && iconMarkup}
                    <span>{item.label}</span>
                </a>
                <ul key={key * 103} className={`dropdown-menu ${this.state.selectedSubMenu === item.id && this.state.expandSubMenu ? "show" : ""}`}>
                    {item.submenu.map((subitem: MenuItem, subindex: number) => this.createSubMenu(subitem, subindex))}
                </ul>
                </li>
            );
        }
        else {
            return (
                <NavItem
                    menuitem={item}
                    menu_id={key}
                    is_active={isActive}
                    submenu_toggle={this.toggleSubMenu}
                    click_on_app={this.clickOnApp}
                    key={key * 104}
                    dataAttributes={dataAttributes}
                />
            );
        }
    };

    private applyTheme = (): ReactNode => {
        const args: PythonArgs = this.props.args;

        const mergedTheme = {
            menu_background: this.theme.backgroundColor,
            txc_inactive: this.theme.textColor,
            txc_active: this.theme.textColor,
            option_active: this.theme.primaryColor
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
                --option_active_opacity: ${this.theme.primaryColor}99;
                --option_active_translucent: ${this.theme.primaryColor}38;
            }
            `}
        </style>
        );
    };

    public render = (): ReactNode => {
        const args: PythonArgs = this.props.args;

        const menuItems = this.addHomeLogin();
        const menuLook = args.use_animation ? "complexnavbarSupportedContent" : "navbarSupportedContent";

        // const selector = args.use_animation ? (
        //   <div className="hori-selector">
        //     <div className="left"></div>
        //     <div className="right"></div>
        //   </div>
        // ) : null;

        return (
            <StyletronProvider value={engine}>
                <BaseProvider theme={LightTheme}>
                    <div key={args.key}>
                        {this.applyTheme()}
                        <nav className="navbar navbar-expand-custom navbar-mainbg w-100 py-0 py-md-0">
                        <button
                            className="navbar-toggler"
                            type="button"
                            onClick={this.toggleNav}
                            aria-expanded={this.state.expandState}
                        >
                            <span className="material-symbols-rounded text-color">menu</span>
                        </button>
                        <div id={menuLook} className="navbar-collapse" style={{ display: this.state.blockState }}>
                            <ul className="navbar-nav py-0">
                            {menuItems.map((item: MenuItem, index: number) => this.createMenu(item, index))}
                            </ul>
                        </div>
                        </nav>
                    </div>
                </BaseProvider>
            </StyletronProvider>
        );
    };

    // return render();
};

export default withStreamlitConnection(NativeNavBar);
// export default NativeNavBar;
