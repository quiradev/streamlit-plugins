import React from "react";

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

export interface NavItemProps {
  menuitem: MenuItem;
  menu_id: number;
  position_mode: "top" | "under" | "side" | "static" | "hidden";
  is_active: boolean;
  submenu_toggle: (parentId: string) => void;
  click_on_app: (item: MenuItem) => void;
  dataAttributes?: Record<string, string>;
}

const NavItem: React.FC<NavItemProps> = (props: NavItemProps) => {
  const { menuitem, menu_id, position_mode, is_active, submenu_toggle, click_on_app, dataAttributes } = props;

  const containsEmojis = (input: string): boolean => {
    if (!input) return false;
    for (const c of input) {
      const cHex = c.codePointAt(0);
      if (!cHex) continue;
      const sHex = cHex.toString(16);
      const lHex = sHex.length;
      if (lHex <= 3) continue;
      const prefix = sHex.substring(0, 2);
      if (lHex === 5 && prefix === "1f") return true;
      if (lHex === 4 && ["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].includes(prefix))
        return true;
    }
    return false;
  };

  const onSelect = () => {
    submenu_toggle("");
    click_on_app(menuitem);
  };

  const label = menuitem.label;
  const hasIcon = !!menuitem.icon;

  let iconContent = "";
  if (position_mode === "side") {
    iconContent = label.charAt(0).toUpperCase();
  }
  let iconMarkup: React.ReactNode = <span className="icon icon-placeholder">{iconContent}</span>;

  if (hasIcon) {
    const regex = /:material\/(\w+):/gm;
    const iconStr = menuitem.icon || "";
    const m = regex.exec(iconStr);
    if (m !== null) {
      iconMarkup = <span className="material-symbols-rounded icon">{m[1]}</span>;
    } else {
      const iconClass = containsEmojis(iconStr) ? "icon" : `${iconStr} icon`;
      const iconTxt = containsEmojis(iconStr) ? iconStr : "";
      iconMarkup = <i className={iconClass}>{iconTxt}</i>;
    }
  }

  const style = menuitem.style as React.CSSProperties || {};

  return (
    <li style={style} className={`nav-item py-0 ${is_active ? "active" : ""}`} key={menu_id} {...dataAttributes}>
      <a
        className="nav-link"
        href={"#" + menu_id}
        onClick={() => onSelect()}
        data-toggle="tooltip"
        data-placement="top"
        data-html="true"
        title={menuitem.ttip}
      >
        {iconMarkup}
        <span>{label}</span>
      </a>
    </li>
  );
};

export default NavItem;
