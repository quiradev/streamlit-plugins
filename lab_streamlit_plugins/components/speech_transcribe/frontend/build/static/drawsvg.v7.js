// This contains the code that renders and controls the visualization.

const get_sunburst_render_params = () => {
  // 80% of the smallest window dimension
  var width = 0.8 * Math.min(window.innerHeight, window.innerWidth);
  var height = width;
  var radius = width / 2;
  var partition = d3.partition()
    .size([2 * Math.PI, radius * radius])
    .padding(0)
    .round(true)
    .value(d => d.time);
  // By default D3 makes the y size proportional to some area,
  // so y is a transformation from ~area to a linear scale
  // so that all arcs have the same radial size.
  var y = d3.scaleLinear().domain([0, radius * radius]).range([0, radius]);
  var arc = d3.arc()
    .startAngle(d => Math.max(0, Math.min(2 * Math.PI, d.x0)))
    .endAngle(d => Math.max(0, Math.min(2 * Math.PI, d.x1)))
    .innerRadius(d => y(d.y0))
    .outerRadius(d => y(d.y1));
  return {
    "width": width,
    "height": height,
    "radius": radius,
    // "transform": "translate(" + radius + "," + radius + ")",
    "partition": partition,
    "arc": arc
  };
};

const get_icicle_render_params = () => {
  var width = window.innerWidth * 0.75;
  // var height = window.innerHeight * 0.8;
  var height = 500;
  // var height = $("#chart").innerHeight();
  var leftMargin = 90;
  var topMargin = 60;
  var partition = d3.partition()
    .size([width - leftMargin, height - topMargin])
    .padding(0)
    .round(true)
    .value(d => d.time);
  return {
    "width": width,
    "height": height,
    "leftMargin": leftMargin,
    "topMargin": topMargin,
    // "transform": "translate(" + leftMargin + "," + topMargin + ")",
    "partition": partition
  };
};

const get_render_params = style => {
  if (style === "sunburst") {
    return get_sunburst_render_params();
  } else if (style === "icicle") {
    return get_icicle_render_params();
  } else {
    throw new Error("Unknown rendering style '" + style + "'.");
  }
};

// Colors.
var colorScheme = d3.schemeSet2;
var colorScale = d3.scaleOrdinal(colorScheme);
var vis;

// should make it so that a given function is always the same color
const color = d => colorScale(d.name);

const make_vis_obj = style => {
  const params = get_render_params(style);
  return d3.select("#chart")
    .style('margin-left', 'auto')
    .style('margin-right', 'auto')
    .append("svg")
    .attr("width", params.width)
    .attr("height", params.height)
    .append("g")
    .attr("id", "container")
    .attr("transform", `translate(${params.radius}, ${params.radius})`);
};

const reset_vis = style => {
  // Remove the current figure
  d3.select('svg').remove();

  // Make and draw the new svg container
  vis = make_vis_obj(style);
};

// This is the function that runs whenever the user clicks on an SVG
// element to trigger zooming.
const click = (event, d) => {
  // check whether we need to do anything
  // (e.g. that the user hasn't clicked on the original root node)
  if (d.name === sv_root_func_name) {
    return;
  }

  const stack_last = sv_call_stack[sv_call_stack.length - 1];
  let new_root;
  if (d.name === stack_last) {
    // need to go up a level in the call stack
    sv_call_stack.pop();
    new_root = sv_call_stack[sv_call_stack.length - 1];
  } else {
    new_root = d.name;

    // need to construct a new call stack
    // go up the tree until we hit the tip of the call stack
    let this_node = d;
    const local_stack = [new_root];
    while (this_node.parent != null) {
      if (this_node.parent.name === stack_last) {
        // extend the call stack with what we've accumulated
        local_stack.reverse();
        sv_call_stack = sv_call_stack.concat(local_stack);
        break;
      } else {
        local_stack.push(this_node.parent.name);
        this_node = this_node.parent;
      }
    }
  }

  //figure out the new parent name
  let new_parent_name;
  if (sv_call_stack.length === 1) {
    new_parent_name = null;
  } else {
    new_parent_name = sv_call_stack[sv_call_stack.length - 2];
  }

  // Create new JSON for drawing a vis from a new root
  sv_draw_vis(new_root, new_parent_name);
  sv_update_call_stack_list();

  // Activate the reset button if we aren't already at the root node
  // And deactivate it if this is the root node
  if (new_root !== sv_root_func_name) {
    d3.select('#resetbutton-zoom').attr('disabled', null);
  } else {
    d3.select('#resetbutton-zoom').attr('disabled', true);
  }
};

const sv_info_tpl = _.template(
  ['<div class="sv-info-label"><span>Name</span><span class="sv-info-item"><%- name %></span></div>',
   '<div class="sv-info-label"><span>Cumulative Time</span><span class="sv-info-item"><%= cumulative %> s (<%= cumulative_percent %> %)</span></div>',
   '<div class="sv-info-label"><span>File</span><span class="sv-info-item"><%- file %></span></div>',
   '<div class="sv-info-label"><span>Line</span><span class="sv-info-item"><%= line %></span></div>',
   '<div class="sv-info-label"><span>Directory</span><span class="sv-info-item"><%- directory %></span></div>'
  ].join('\n')
);

const sv_update_info_div = d => {
  const re = /^(.*):(\d+)\((.*)\)$/;
  const result = re.exec(d.data.name);
  const file = result[1];
  let directory = '';
  const slash = file.lastIndexOf('/');
  if (slash !== -1) {
    directory = file.slice(0, slash + 1);
    file = file.slice(slash + 1);
  }
  const info = {
    'file': file,
    'directory': directory,
    'line': result[2],
    'name': result[3],
    'cumulative': d.data.cumulative.toPrecision(3),
    'cumulative_percent': (d.data.cumulative / sv_total_time * 100).toFixed(2)
  };

  const style = d3.select('#sv-style-select').property('value');
  const div = d3.select('#sv-info-div');
  div.html(sv_info_tpl(info));

  const { radius } = get_sunburst_render_params();
  if ((style === 'sunburst') && (!div.classed('sunburst'))) {
    div
      .classed('sunburst', true)
      .classed('icicle', false)
      .style('height', `${radius * 1.5}px`)
      .style('width', `${($('body').width() - (2 * radius)) / 2.1}px`);
  } else if ((style === 'icicle') && (!div.classed('icicle'))) {
    div
      .classed('icicle', true)
      .classed('sunburst', false)
      .style('height', `${radius * 1.5}px`)
      .style('width', '200px');
  }
};

const apply_mouseover = selection => {
  selection.on('mouseover', function(event, d) {
    // select all the nodes that represent this exact function
    // and highlight them by darkening their color
    const thisname = d.name;
    const thispath = selection.filter(function(d) {
        return d.name === thisname;
    });
    const thiscolor = d3.rgb('#ff00ff');
    thispath.style('fill', thiscolor.toString());
    sv_update_info_div(d);
    sv_show_info_div();
  })
  .on('mouseout', function(event, d){
      // reset nodes to their original color
      const thisname = d.name;
      const thispath = selection.filter(function(d) {
          return d.name === thisname;
      });
      thispath.style('fill', color(d));
  });
};

// This is having D3 do its thing.
const drawSunburst = json => {
  const params = get_render_params("sunburst");

  // For efficiency, filter nodes to keep only those large enough to see.
  const nodes = params["partition"](json).descendants().filter(function(d) {
    return (d.dx > 0.005); // 0.005 radians = 0.29 degrees.
  });

  // Bounding circle underneath the sunburst, to make it easier to detect
  // when the mouse leaves the parent g.
  vis.append("circle")
    .attr("r", params["radius"])
    .style("opacity", 0);

  const path = vis.selectAll("path")
    .data(nodes)
    .join("path")
    .attr("id", function(d, i) { return "path-" + i; })
    .attr("d", params["arc"])
    .attr("fill-rule", "evenodd")
    .style("fill", d => color(d))
    .on('click', click)
    .call(apply_mouseover);
};


const drawIcicle = json => {
  const params = get_render_params("icicle");
  const nodes = params["partition"](json).descendants().filter(function(d) {
    return (d.dx > 0.5); // at least half-a-pixel wide to be visible.
  });
  const x = d3.scaleLinear()
      .domain([0, nodes[0].dx])
      .range([0, params["width"] - params["leftMargin"]]);
  const y = d3.scaleLinear()
      .domain([0, nodes[0].dy * $('#sv-depth-select').val()])
      .range([0, params["height"] - params["topMargin"]]);

  const rect = vis.selectAll("rect")
      .data(nodes)
      .join("rect")
      .attr("id", (d, i) => `path-${i}`)
      .attr("x", (d) => x(d.x0))
      .attr("y", (d) => y(d.y0))
      .attr("width", (d) => x(d.x1 - d.x0))
      .attr("height", (d) => y(d.y1 - d.y0))
      .attr("fill-rule", "evenodd")
      .attr("fill", color)
      .on('click', click)
      .call(apply_mouseover);

  const labels = vis.selectAll("text")
        .data(nodes)
        .join("text")
        .attr("x", (d) => x(d.x0 + (d.x1 - d.x0) / 2))
        .attr("y", (d) => y(d.y0 + (d.y1 - d.y0) / 2))
        .attr("width", (d) => x(d.x1 - d.x0))
        .attr("height", (d) => y(d.y1 - d.y0))
        .attr("font-family", "sans-serif")
        .attr("font-size", "15px")
        .attr("fill", "black")
        .attr("text-anchor", "middle")
        .attr("pointer-events", "none");

  // Append the function name
  labels.append("tspan")
    .text((d) => d.data.display_name)
    .attr("text-anchor", "middle")
    .attr("x", (d) => x(d.x0 + (d.x1 - d.x0) / 2));
  // Append the time
  labels.append("tspan")
    .text((d) => `${d.data.cumulative.toPrecision(3)} s`)
    .attr("text-anchor", "middle")
    .attr("x", (d) => x(d.x0 + (d.x1 - d.x0) / 2))
    .attr("dy", "1.2em");

  // Remove labels that don't fit
  vis.selectAll("text")
    .filter((d) => this.getBBox().width > x(d.x1 - d.x0))
    .remove();

  d3.select("#chart svg").attr("height", d3.select("svg g#container").node().getBBox().height);
};

// Clear and redraw the visualization
const redraw_vis = json => {
  const style = $('#sv-style-select').val();
  reset_vis(style);
  if (style === "sunburst") {
    drawSunburst(json);
  } else if (style === "icicle") {
    drawIcicle(json);
  }
  d3.select('#container')
    .on('mouseenter', sv_show_info_div)
    .on('mouseleave', sv_hide_info_div);
};


// Reset the visualization to its original state starting from the
// main root function.
const resetVis = () => {
  sv_draw_vis(sv_root_func_name);

  // Reset the call stack
  sv_call_stack = [sv_root_func_name];
  sv_update_call_stack_list();

  $('#resetbutton-zoom').prop('disabled', true);
};


const resetRoot = () => {
  // originally set in the setup code in viz.html
  sv_root_func_name = sv_root_func_name__cached;
  resetVis();
  $('#resetbutton-root').prop('disabled', true);
};


// The handler for when the user changes the depth selection dropdown.
const sv_selects_changed = () => {
  sv_cycle_worker();
  var parent_name = null;
  if (sv_call_stack.length > 1) {
    parent_name = sv_call_stack[sv_call_stack.length - 2];
  }
  sv_hide_error_msg();
  sv_draw_vis(sv_call_stack[sv_call_stack.length - 1], parent_name);
};

window.init_d3_listeners = () => {
  vis = make_vis_obj("sunburst");
  $('#resetbutton-zoom').on('click', resetVis);
  $('#resetbutton-root').on('click', resetRoot);
  d3.select('#sv-style-select').on('change', sv_selects_changed);
  d3.select('#sv-depth-select').on('change', sv_selects_changed);
  d3.select('#sv-cutoff-select').on('change', sv_selects_changed);
}
