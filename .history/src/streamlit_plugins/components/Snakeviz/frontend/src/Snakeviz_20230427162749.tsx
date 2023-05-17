import { Streamlit, Theme, RenderData } from "streamlit-component-lib";
import React, { ReactNode, useState } from "react";
import { useRenderData } from "./Provider";
import NavItem from "./NavItem.jsx";
import NavSubItem from "./NavSubItem.jsx";
import "./snakeviz.js"
import "./drawsvg.js"


type TableRows = Array<Array<Array<string | number | Array<string>>>>;
type Callees = Record<string, Record<string, any>>;

interface PythonArgs {
  table_rows: TableRows,
  callees: Callees,
  profile_name: string
}

interface NavBarRenderData extends RenderData {
  args: PythonArgs;
  disabled: boolean;
  theme?: Theme;
}

const Snakeviz: React.VFC = () => {
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
  let table_data: TableRows = args.table_rows;
  let callees: Callees = args.callees;
  let profile_name: string = args.profile_name;

  window.stats = callees;

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



  const snakeviz = (): ReactNode => {
    return (
      <div>
        <h1 id="snakeviz-text">
          <a href="https://jiffyclub.github.io/snakeviz/">SnakeViz</a>
        </h1>

        <span id="resetbuttons">
          <div className="button-div">
            <button id="resetbutton-root" disabled="True">Reset Root</button>
          </div>
          <div className="button-div">
            <button id="resetbutton-zoom" disabled="True">Reset Zoom</button>
          </div>
        </span>

        <label id='sv-style-label'>Style:&nbsp;
          <select name="sv-style" id="sv-style-select">
            <option value="icicle" selected>Icicle</option>
            <option value="sunburst">Sunburst</option>
          </select>
        </label>

        <label id='sv-depth-label'>Depth:&nbsp;
          <select name="sv-depth" id="sv-depth-select">
            {
              [3, 5, 10, 15, 20].map((i: int, index: number) => (
                <option value={i} selected={i === 10}>{i}</option>
              )
            )}
          </select>
        </label>

        <label id='sv-cutoff-label'>Cutoff:
          <select name="sv-cutoff" id="sv-cutoff-select">
            <option value="0.001" selected>1 &frasl; 1000</option>
            <option value="0.01">1 &frasl; 100</option>
            <option value="0">None</option>
          </select>
        </label>

        <div id="sv-info-div"></div>

        <div id="sv-call-stack">
          <div id="working-spinner" className="spinner">
            <div className="bounce1"></div>
            <div className="bounce2"></div>
            <div className="bounce3"></div>
          </div>
          <div style={{ "display": "inline-block" }}>
            <button id="sv-call-stack-btn">Call Stack</button>
          </div>
          <div id="sv-call-stack-list"></div>
        </div>

        <div id="sv-error-div" className="sv-error-msg">
          <p>
            An error occurred processing your profile.
            You can try a lower depth, a larger cutoff,
            or try profiling a smaller portion of your code.
            If you continue to have problems you can
            <a href="https://github.com/jiffyclub/snakeviz/issues">
              contact us on GitHub</a>.
          </p>
          <div id="sv-error-close-div" className="sv-error-close">Close</div>
        </div>

        <div style={{ "text-align": "center" }}>
          <div id="chart"></div>
        </div>

        <div id="table_div">
          <table cellpadding="0" cellspacing="0" border="0" className="display" id="pstats-table">
            <thead>
              <tr>
                <th title="Total number of calls to the function. If there are two numbers, that means the function recursed and the first is the total number of calls and the second is the number of primitive (non-recursive) calls.">ncalls</th>
                <th title="Total time spent in the function, not including time spent in calls to sub-functions.">tottime</th>
                <th title="`tottime` divided by `ncalls`">percall</th>
                <th title="Cumulative time spent in this function and all sub-functions.">cumtime</th>
                <th title="`cumtime` divided by `ncalls`">percall</th>
                <th title="File name and line number were the function is defined, and the function’s name.">filename:lineno(function)</th>
              </tr>
            </thead>
          </table>
        </div>

        <footer className="sv-footer">
          <a className="footer-link" href="https://jiffyclub.github.io/snakeviz/">SnakeViz Docs</a>
        </footer>
      </div>
    );
  };

  const loseFocus = (): void => {
    document.addEventListener('focusout', event => {
      setTimeout(
      () => {
          if (!document.clickInside) {
            console.log("FOCUSOUT FIRE");
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
  const initListeners = (): void => {
    // Make the stats table
    // var table_data = {% raw table_rows %};

    $(document).ready(function() {
      var table = $('#pstats-table').dataTable({
        'data': table_data,
        'columns': [
          // Note: columns are also defined in #pstats-table in HTML above,
          // this list must line up with that.
          {'type': 'num', 'searchable': 'false',
           'data': {
            '_': function (row: any) {return row[0][0];},
            'sort': function (row: any) {return row[0][1]}
           }},
          {'type': 'num', 'searchable': 'false'},
          {'type': 'num', 'searchable': 'false'},
          {'type': 'num', 'searchable': 'false'},
          {'type': 'num', 'searchable': 'false'},
          {}
        ],
        'order': [1, 'desc'],
        'paging': false
      }).api();
      $('#pstats-table tbody').on('click', 'tr', function() {
        var name = table.row(this).data()[6];
        sv_root_func_name = name;
        sv_draw_vis(name);
        sv_call_stack = [name];
        sv_update_call_stack_list();
        $('#resetbutton-zoom').prop('disabled', true);
        $('#resetbutton-root').prop('disabled', false);
      }).on('mouseenter', 'tr', function () {
        $(this).children('td').addClass('data-table-hover');
      }).on('mouseleave', 'tr', function () {
        $(this).children('td').removeClass('data-table-hover');
      });

      var profile_data = callees;
      sv_json_cache = {};
      sv_worker = sv_make_worker();
      sv_root_func_name = sv_find_root(profile_data);
      sv_root_func_name__cached = sv_root_func_name;
      sv_call_stack = [sv_root_func_name];
      sv_total_time = profile_data[sv_root_func_name]['stats'][3];

      sv_update_call_stack_list();
      sv_call_stack_btn_for_show();

      sv_draw_vis(sv_root_func_name);
    });

    // Initialize data
    //$(document).ready(_.defer(function () {
      
    //}));
    // Initialize the call stack button
    //$(document).ready(_.defer(function () {
      
    //}));
    // Draw the visualization
    //$(document).ready(_.defer(function () {
      
    //}));
  }

  // DEFINE LISTENERSE ONE TIME
  if (!document.definedListeners) document.definedListeners = false;
  if (!document.clickInside) document.clickInside = false;
  if (!document.definedListeners) {
      document.definedListeners = true
      loseFocus();
      initListeners();
  }
  return snakeviz();
};

//export default withStreamlitConnection(NavBar);
export default Snakeviz;
