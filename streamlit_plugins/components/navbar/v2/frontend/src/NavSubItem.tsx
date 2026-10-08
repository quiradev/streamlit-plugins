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

export interface NavSubItemProps {
  subitem: MenuItem;
  menu_id: number;
  parent_id: string;
  is_active: boolean;
  submenu_toggle: (parentId: string) => void;
  click_on_app: (item: MenuItem) => void;
}

const NavSubItem: React.FC<NavSubItemProps> = (props: NavSubItemProps) => {
  const { subitem, menu_id, parent_id, is_active, submenu_toggle, click_on_app } = props;

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
    submenu_toggle(parent_id);
    click_on_app(subitem);
  };

  const label = subitem.label;
  const hasIcon = !!subitem.icon;

  let iconMarkup: React.ReactNode = null;
  if (hasIcon) {
    const regex = /:material\/(\w+):/gm;
    const iconStr = subitem.icon || "";
    const m = regex.exec(iconStr);
    if (m !== null) {
      iconMarkup = <span className="material-symbols-rounded icon">{m[1]}</span>;
    } else {
      const iconClass = containsEmojis(iconStr) ? "icon" : `${iconStr} icon`;
      const iconTxt = containsEmojis(iconStr) ? iconStr : "";
      iconMarkup = <i className={iconClass}>{iconTxt}</i>;
    }
  }

  return (
    <li className={is_active ? "active" : ""} key={parent_id + menu_id * 97}>
      <a
        className="dropdown-item"
        href={"#" + menu_id * 97}
        onClick={() => onSelect()}
        data-toggle="tooltip"
        data-placement="top"
        data-html="true"
        title={subitem.ttip}
      >
        {hasIcon && iconMarkup}
        <span>{label}</span>
      </a>
    </li>
  );
};

export default NavSubItem;
