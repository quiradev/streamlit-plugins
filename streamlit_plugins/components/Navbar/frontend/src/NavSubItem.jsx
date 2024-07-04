import React from "react"
import "./bootstrap.min.css"

const NavSubItem = (props) => {
  let menu_subitem = props.subitem;
  let menu_id = props.menuid;
  let parent_id = props.parent_id;
  let is_active = props.is_active;
  const submenu_toggle = props.submenu_toggle;
  const click_on_app = props.click_on_app;

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

  const onSelect = (item_id: string, subitem_id: string) => {
    submenu_toggle(item_id);
    click_on_app(item_id, subitem_id);
  }

  const create_submenuitem = (item, kid, parent_id) => {
      let label = "";
      let iconClass = "";
      let iconTxt = "";
      if (containsEmojis(item.icon)) {
        iconTxt = item.icon
        label = item.label;
      } else {
        iconClass = item.icon;
        label = item.label;
      }

      return (
        <li className={is_active ? "active": ""} key={parent_id+kid*97}>
            <a className="dropdown-item" href={"#" + kid*97} onClick={()=>onSelect(parent_id, item.id)} data-toggle="tooltip" data-placement="top" data-html="true" title={item.ttip}>
                <i className={iconClass}>{iconTxt}</i>
                <span>{label}</span>
            </a>
        </li>
      );
  }
  
  return create_submenuitem(menu_subitem, menu_id, parent_id);

}

export default NavSubItem