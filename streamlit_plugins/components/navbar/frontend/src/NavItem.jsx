import React from "react"
// import "./bootstrap.min.css"

const NavItem = (props) => {
  let menu_item = props.menuitem;
  let is_active = props.is_active;
  let menu_id = props.menu_id;
  let position_mode = props.position_mode;
  const submenu_toggle = props.submenu_toggle;
  const click_on_app = props.click_on_app;
  const dataAttributes = props.dataAttributes;

  const containsEmojis = (input) => {
    if (input) {
      for (var c of input) {
          var cHex = ("" + c).codePointAt(0);
          if(cHex) {
          var sHex = cHex.toString(16);
          var lHex = sHex.length;
            if (lHex > 3) {

                var prefix = sHex.substring(0, 2);

                if (lHex === 5 && prefix === "1f") {
                    return true;
                }

                if (lHex === 4) {
                    if (["20", "21", "23", "24", "25", "26", "27", "2B", "29", "30", "32"].indexOf(prefix) > -1)
                        return true;
                }
            }
        }
      }
    }

    return false;
  }

  const onSelect = () => {
    submenu_toggle("");
    click_on_app(menu_item);
  }

  const create_item = (item, kid, is_active) => {
    const label = item.label;
    const hasIcon = item.icon ? true : false;

    // Me quedo con la primera letra de label para el icono
    let iconContent = ""
    if (position_mode === "side") {
        iconContent = item.label.charAt(0).toUpperCase()
    }
    let iconMarkup = <span className="icon icon-placeholder">{iconContent}</span>;

    // Determinar si se usa <i> o <span> para el icono
    if (hasIcon) {
        const regex = /:material\/(\w+):/gm;
        const m = regex.exec(item.icon);
        if (m !== null) {
            const symbol = m[1];
            iconMarkup = <span className="material-symbols-rounded icon">{symbol}</span>;
        }
        else {
            const iconClass = containsEmojis(item.icon) ? "icon" : `${item.icon} icon`;
            const iconTxt = containsEmojis(item.icon) ? item.icon : "";
            iconMarkup = <i className={iconClass}>{iconTxt}</i>;
        }
    }

    return (
      <li style={item.style || {}} className={`nav-item py-0 ${is_active ? "active": ""}`} key={kid} {...dataAttributes}>
        <a className="nav-link" href={"#" + kid} onClick={()=>onSelect()} data-toggle="tooltip" data-placement="top" data-html="true" title={item.ttip}>
          {iconMarkup}
          <span>{label}</span>
        </a>
      </li>
    );
  }
  
  return create_item(menu_item, menu_id, is_active);

}

export default NavItem