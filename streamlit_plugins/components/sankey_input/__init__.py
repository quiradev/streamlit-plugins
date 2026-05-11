from typing import Optional, List, Dict, Any
import streamlit as st
from streamlit.components import v2
from streamlit.components.v2.types import ComponentRenderer

_HTML = """
<div class="sankey-container">
    <div class="sankey-card">
        <svg id="sankey-svg" viewBox="0 0 950 550">
            <defs id="svg-defs">
                <filter id="gooey" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="3.5" result="blur"/>
                    <feColorMatrix in="blur" mode="matrix"
                        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -8"
                        result="goo"/>
                </filter>
            </defs>
            <g id="layer-inactive" class="layer-inactive"></g>
            <g id="layer-active" class="layer-active"></g>
            <g id="layer-hover-basic"></g>
            <g id="layer-nodes"></g>
        </svg>
    </div>
</div>
"""

_CSS = """
.sankey-container {
    --bg-color: #f0f2f5;
    --panel-bg: #ffffff;
    --text-main: #2d3436;
    --text-light: #636e72;
    --inactive-gray: #dfe6e9;
    --inactive-node: #b2bec3;
    --group-bg: #f8f9fa;
    --group-border: #dcdde1;
    --op-inactive: 0.5;
    --op-suggest: 0.2;
    --op-partial: 0.35;
    --op-active: 0.8;
}

.sankey-container {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--text-main);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 0;
}

.sankey-container.is-presentation .sankey-node,
.sankey-container.is-presentation .group-item,
.sankey-container.is-presentation .route-group { pointer-events: none !important; }

.sankey-container.is-view-only .route-group,
.sankey-container.is-view-only .sankey-node,
.sankey-container.is-view-only .group-item {
    cursor: default;
}

.sankey-card {
    background: var(--panel-bg);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    width: 95%;
    max-width: 1100px;
    box-sizing: border-box;
    overflow-x: auto;
}

#sankey-svg { width: 100%; height: auto; min-width: 600px; display: block; }

.gooey-group-inactive { opacity: var(--op-inactive); filter: none; }
.gooey-group-active { opacity: var(--op-active); filter: none; }

.gooey-group-inactive:has(path:not([style*="display: none"]) ~ path:not([style*="display: none"])) { filter: url(#gooey); }
.gooey-group-active:has(path:not([style*="display: none"]) ~ path:not([style*="display: none"])) { filter: url(#gooey); }

.path-inactive { fill: none; stroke: var(--inactive-gray); }
.path-active { fill: none; display: none; }

.route-group { cursor: pointer; }
.route-segment { fill: none; stroke: var(--inactive-gray); stroke-opacity: 0; transition: stroke-opacity 0.2s ease; }
.route-group:hover .route-segment { stroke-opacity: var(--op-active) !important; filter: drop-shadow(0 0 4px rgba(0,0,0,0.2)); }
.route-group:not(:hover).is-node-hovered .route-segment { stroke-opacity: var(--op-partial) !important; }
.layer-hover-basic { opacity: 1; }
.route-group:not(:hover).is-partial .route-segment { stroke-opacity: var(--op-partial) !important; }
.route-group:not(:hover):not(.is-node-hovered).is-suggested .route-segment { stroke-opacity: var(--op-suggest) !important; }
.route-group.is-node-hovered .route-segment { stroke-opacity: 0.3 !important; }

.sankey-node { cursor: pointer; transform-origin: center; transform-box: fill-box; transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1); }
.sankey-node:hover { transform: scale(1.03); }
.sankey-node .node-bar { fill: var(--inactive-node); transition: fill 0.3s ease; }

.label-bg { fill: rgba(30,39,46,0.85); stroke: rgba(255,255,255,0.1); stroke-width: 1px; pointer-events: none; transition: fill 0.3s; }
.sankey-node.active .label-bg { fill: rgba(0,0,0,0.95); }
.node-label-text { fill: white; font-size: 11px; font-weight: 600; pointer-events: none; text-anchor: middle; dominant-baseline: middle; }

.group-container { fill: var(--group-bg); stroke: var(--group-border); stroke-width: 2px; }
.group-main-bar, .group-item-bar { transition: fill 0.3s ease; }
.group-title { fill: var(--text-light); font-size: 11px; font-weight: bold; text-anchor: middle; letter-spacing: 1px; text-transform: uppercase; }

.group-item { cursor: pointer; }
.group-item rect.hitbox { fill: transparent; transition: background 0.2s; }
.group-item:hover rect.hitbox { fill: rgba(0,0,0,0.05); }
.group-item text { fill: var(--text-main); font-size: 13px; dominant-baseline: middle; pointer-events: none; font-weight: 500; }

.item-icon { fill: white; stroke: var(--inactive-node); stroke-width: 2px; transition: all 0.2s; }
.item-icon.radio { rx: 50%; ry: 50%; }
.item-icon.checkbox { rx: 3px; ry: 3px; }
"""

_JS = """
export default function({ parentElement, data, setStateValue }) {
    const DEFAULT_COLORS = ["#ff7675", "#74b9ff", "#55efc4", "#fdcb6e", "#a55eea"];

    const APP_CONFIG = {
        useGradients: true,
        showSuggestions: true,
        singlePath: false,
        convergeGroup: undefined,
        opInactive: 0.5,
        opSuggest: 0.2,
        opPartial: 0.35,
        opActive: 0.8,
        columnColors: DEFAULT_COLORS,
        ...(data?.app_config || {})
    };

    const rawConfig = data?.config || [];
    const config = rawConfig.map((col, i) => ({
        color: APP_CONFIG.columnColors[i % APP_CONFIG.columnColors.length],
        ...col
    }));

    const PRESENTATION = data?.presentation || false;
    const VIEW_ONLY = PRESENTATION || !!data?.view_only || !!APP_CONFIG.viewOnly;

    const DIAGRAM_OPTIONS = {
        marginTop: 60, marginBottom: 60, marginLeft: 40, marginRight: 40,
        minNodeGapY: 35, columnSpacing: 180,
        ...(data?.diagram_options || {})
    };

    const PATH_THICKNESS = data?.path_thickness || 12;
    const NORMAL_NODE_WIDTH = data?.normal_node_width || 20;
    const GROUP_WIDTH = data?.group_width || 170;

    const container = parentElement.querySelector(".sankey-container");
    if (PRESENTATION && container) container.classList.add("is-presentation");
    if (VIEW_ONLY && container) container.classList.add("is-view-only");
    container.style.setProperty("--op-inactive", String(APP_CONFIG.opInactive));
    container.style.setProperty("--op-suggest", String(APP_CONFIG.opSuggest));
    container.style.setProperty("--op-partial", String(APP_CONFIG.opPartial));
    container.style.setProperty("--op-active", String(APP_CONFIG.opActive));

    const defsLayer = parentElement.querySelector("#svg-defs");
    const inactiveLayer = parentElement.querySelector("#layer-inactive");
    const activeLayer = parentElement.querySelector("#layer-active");
    const hoverBasicLayer = parentElement.querySelector("#layer-hover-basic");
    const nodesLayer = parentElement.querySelector("#layer-nodes");

    let SVG_WIDTH = 0, SVG_HEIGHT = 0;
    let isSinglePathMode = !!APP_CONFIG.singlePath;
    let isGroupConvergeMode = false;
    let selections = config.map(() => []);
    const storageKey = data?.selection_storage_key || `sankey_input:${data?.component_key || "default"}`;

    const groupCol = config.find((c) => c.type === "group");
    if (groupCol && typeof APP_CONFIG.convergeGroup === "boolean") {
        groupCol.converge = APP_CONFIG.convergeGroup;
    }

    function sanitizeSelections(rawSelections) {
        const incoming = Array.isArray(rawSelections) ? rawSelections : [];
        return config.map((col, colIdx) => {
            const validIds = new Set((col.nodes || []).map((n) => n.id));
            const source = Array.isArray(incoming[colIdx]) ? incoming[colIdx] : [];
            const filtered = source.filter((id) => validIds.has(id));
            if (isSinglePathMode && col.type !== "group") return filtered.slice(0, 1);
            return filtered;
        });
    }

    function readSelectionsFromLocalStorage() {
        try {
            const raw = window.localStorage.getItem(storageKey);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed) ? parsed : null;
        } catch (error) {
            return null;
        }
    }

    function saveSelectionsToLocalStorage(nextSelections) {
        try {
            window.localStorage.setItem(storageKey, JSON.stringify(nextSelections));
        } catch (error) {
            // No-op: localStorage puede estar bloqueado por el navegador.
        }
    }

    const hasInitialSelections = Array.isArray(data?.initial_selections);
    const initialSourceSelections = hasInitialSelections
        ? data.initial_selections
        : (readSelectionsFromLocalStorage() || []);
    selections = sanitizeSelections(initialSourceSelections);
    saveSelectionsToLocalStorage(selections);

    let nodesDataMap = {}, allPaths = [], nodePaths = {}, sourceGroups = {},
        activePathElements = {}, inactivePathElements = {};
    let convergentPathsY = {};
    const createdGradients = new Set();

    function init() {
        inactiveLayer.innerHTML = "";
        activeLayer.innerHTML = "";
        hoverBasicLayer.innerHTML = "";
        nodesLayer.innerHTML = "";
        nodesDataMap = {}; allPaths = []; nodePaths = {}; sourceGroups = {};
        activePathElements = {}; inactivePathElements = {};

        for (let i = 1; i < config.length; i++) {
            config[i].nodes.forEach((node) => {
                let sumY = 0, count = 0;
                config[i - 1].nodes.forEach((prevNode, pIdx) => {
                    if (prevNode.targets && prevNode.targets.includes(node.id)) { sumY += pIdx; count++; }
                });
                node.orderScore = count > 0 ? sumY / count : 0;
            });
            config[i].nodes.sort((a, b) => a.orderScore - b.orderScore);
        }

        function generatePaths(currentNodeId, currentPath, colIndex) {
            if (colIndex === config.length - 1) {
                allPaths.push({ id: currentPath.join("-"), nodes: [...currentPath] });
                return;
            }
            const node = config[colIndex].nodes.find((n) => n.id === currentNodeId);
            if (node && node.targets)
                node.targets.forEach((t) => generatePaths(t, [...currentPath, t], colIndex + 1));
        }

        config[0].nodes.forEach((n) => generatePaths(n.id, [n.id], 0));
        config.forEach((col) => col.nodes.forEach((n) => { nodePaths[n.id] = []; }));
        allPaths.forEach((p) => p.nodes.forEach((nodeId) => {
            if (nodePaths[nodeId]) nodePaths[nodeId].push(p);
        }));

        config.forEach((col, colIdx) => {
            if (colIdx === config.length - 1) return;
            col.nodes.forEach((node) => {
                nodePaths[node.id].sort((pA, pB) => {
                    const idxA = config[colIdx + 1].nodes.findIndex((n) => n.id === pA.nodes[colIdx + 1]);
                    const idxB = config[colIdx + 1].nodes.findIndex((n) => n.id === pB.nodes[colIdx + 1]);
                    return idxA - idxB;
                });
            });
        });

        const nodeHeights = {};
        config.forEach((col) => {
            col.nodes.forEach((node) => {
                const flowHeight = nodePaths[node.id].length * PATH_THICKNESS;
                nodeHeights[node.id] = col.type === "radio"
                    ? Math.max(50, flowHeight + 10)
                    : Math.max(34, flowHeight + 12);
            });
        });

        let maxRequiredHeight = 0;
        config.forEach((col) => {
            if (col.type === "radio")
                maxRequiredHeight = Math.max(maxRequiredHeight,
                    col.nodes.reduce((s, n) => s + nodeHeights[n.id], 0) + DIAGRAM_OPTIONS.minNodeGapY * (col.nodes.length - 1));
            else
                maxRequiredHeight = Math.max(maxRequiredHeight,
                    col.nodes.reduce((s, n) => s + nodeHeights[n.id] + 8, 0) + 50);
        });

        SVG_HEIGHT = maxRequiredHeight + DIAGRAM_OPTIONS.marginTop + DIAGRAM_OPTIONS.marginBottom;
        SVG_WIDTH = (config.length - 1) * NORMAL_NODE_WIDTH + GROUP_WIDTH +
            (config.length - 1) * DIAGRAM_OPTIONS.columnSpacing +
            DIAGRAM_OPTIONS.marginLeft + DIAGRAM_OPTIONS.marginRight;

        parentElement.querySelector("#sankey-svg").setAttribute("viewBox", `0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`);

        let currentX = DIAGRAM_OPTIONS.marginLeft;
        config.forEach((col) => {
            col.x = currentX;
            currentX += (col.type === "group" ? GROUP_WIDTH : NORMAL_NODE_WIDTH) + DIAGRAM_OPTIONS.columnSpacing;
        });

        config.forEach((col, colIdx) => {
            const x = col.x;
            if (col.type === "radio") {
                const totalNodesH = col.nodes.reduce((sum, n) => sum + nodeHeights[n.id], 0);
                const availableH = SVG_HEIGHT - DIAGRAM_OPTIONS.marginTop - DIAGRAM_OPTIONS.marginBottom;
                const gap = col.nodes.length > 1 ? (availableH - totalNodesH) / (col.nodes.length - 1) : 0;
                let currentY = DIAGRAM_OPTIONS.marginTop + (col.nodes.length === 1 ? (availableH - totalNodesH) / 2 : 0);

                col.nodes.forEach((node) => {
                    const h = nodeHeights[node.id];
                    nodesDataMap[node.id] = { x, y: currentY, colIdx, width: NORMAL_NODE_WIDTH, height: h };
                    const g = createSVGElement("g", { class: "sankey-node", "data-col": colIdx, "data-id": node.id });
                    g.appendChild(createSVGElement("rect", { x, y: currentY, width: NORMAL_NODE_WIDTH, height: h, class: "node-bar", rx: 6, ry: 6 }));
                    const pillW = node.label.length * 7 + 16, pillH = 24;
                    g.appendChild(createSVGElement("rect", {
                        x: x + NORMAL_NODE_WIDTH / 2 - pillW / 2, y: currentY + h / 2 - pillH / 2,
                        width: pillW, height: pillH, rx: 12, ry: 12, class: "label-bg"
                    }));
                    const text = createSVGElement("text", { x: x + NORMAL_NODE_WIDTH / 2, y: currentY + h / 2 + 1, class: "node-label-text" });
                    text.textContent = node.label;
                    g.append(text);
                    if (!VIEW_ONLY) {
                        g.onclick = () => handleSelection(colIdx, node.id);
                        g.onmouseenter = () => handleNodeHover(node.id, true);
                        g.onmouseleave = () => handleNodeHover(node.id, false);
                    }
                    nodesLayer.appendChild(g);
                    currentY += h + gap;
                });
            } else if (col.type === "group") {
                const groupHeight = col.nodes.reduce((sum, n) => sum + nodeHeights[n.id] + 8, 0) + 50;
                const y = SVG_HEIGHT / 2 - groupHeight / 2;
                const groupCenterY = y + groupHeight / 2;
                const groupG = createSVGElement("g", { class: "sankey-group" });
                groupG.appendChild(createSVGElement("rect", { x, y, width: GROUP_WIDTH, height: groupHeight, class: "group-container" }));
                if (col.converge) {
                    groupG.appendChild(createSVGElement("rect", { x, y, width: NORMAL_NODE_WIDTH / 2, height: groupHeight, fill: "var(--inactive-node)", rx: 4, ry: 4, class: "group-main-bar", "data-col": colIdx }));
                    groupG.appendChild(createSVGElement("rect", { x: x + GROUP_WIDTH - NORMAL_NODE_WIDTH / 2, y, width: NORMAL_NODE_WIDTH / 2, height: groupHeight, fill: "var(--inactive-node)", rx: 4, ry: 4, class: "group-main-bar", "data-col": colIdx }));
                }
                const titleText = createSVGElement("text", { x: x + GROUP_WIDTH / 2, y: y + 25, class: "group-title" });
                titleText.textContent = col.title;
                groupG.appendChild(titleText);
                let itemY = y + 40;
                col.nodes.forEach((node) => {
                    const h = nodeHeights[node.id];
                    nodesDataMap[node.id] = { x, y: itemY, colIdx, width: GROUP_WIDTH, height: h, type: "item", groupCenterY };
                    const itemG = createSVGElement("g", { class: "group-item", "data-col": colIdx, "data-id": node.id });
                    if (!col.converge) {
                        itemG.appendChild(createSVGElement("rect", { x, y: itemY, width: NORMAL_NODE_WIDTH / 2, height: h, fill: "var(--inactive-node)", rx: 4, ry: 4, class: "group-item-bar", "data-col": colIdx, "data-id": node.id }));
                        itemG.appendChild(createSVGElement("rect", { x: x + GROUP_WIDTH - NORMAL_NODE_WIDTH / 2, y: itemY, width: NORMAL_NODE_WIDTH / 2, height: h, fill: "var(--inactive-node)", rx: 4, ry: 4, class: "group-item-bar", "data-col": colIdx, "data-id": node.id }));
                    }
                    itemG.appendChild(createSVGElement("rect", { x, y: itemY, width: GROUP_WIDTH, height: h, class: "hitbox" }));
                    itemG.appendChild(createSVGElement("rect", { x: x + 15, y: itemY + h / 2 - 7, width: 14, height: 14, class: `item-icon ${isSinglePathMode ? "radio" : "checkbox"}` }));
                    const text = createSVGElement("text", { x: x + 40, y: itemY + h / 2 + 1 });
                    text.textContent = node.label;
                    itemG.append(text);
                    if (!VIEW_ONLY) {
                        itemG.onclick = () => handleSelection(colIdx, node.id);
                        itemG.onmouseenter = () => handleNodeHover(node.id, true);
                        itemG.onmouseleave = () => handleNodeHover(node.id, false);
                    }
                    groupG.appendChild(itemG);
                    itemY += h + 8;
                });
                nodesLayer.appendChild(groupG);
            }
        });

        convergentPathsY = {};
        config.forEach((col, colIdx) => {
            if (col.converge && colIdx > 0) {
                let incomingPaths = allPaths.filter((p) => p.nodes[colIdx]);
                incomingPaths.sort((pA, pB) => getPathPortY(pA.nodes[colIdx - 1], pA.id) - getPathPortY(pB.nodes[colIdx - 1], pB.id));
                const groupCenterY = SVG_HEIGHT / 2;
                const totalHeight = incomingPaths.length * PATH_THICKNESS;
                const startY = groupCenterY - totalHeight / 2 + PATH_THICKNESS / 2;
                incomingPaths.forEach((p, idx) => { convergentPathsY[p.id + "-" + colIdx] = startY + idx * PATH_THICKNESS; });
            }
        });

        let segmentGroups = {};
        allPaths.forEach((p) => {
            for (let i = 0; i < p.nodes.length - 1; i++) {
                const sId = p.nodes[i], tId = p.nodes[i + 1];
                const segId = sId + "-" + tId;
                if (!segmentGroups[segId]) segmentGroups[segId] = { sId, tId, colIdx: i, paths: [] };
                segmentGroups[segId].paths.push({ pathId: p.id });
            }
        });

        Object.keys(segmentGroups).forEach((segId) => {
            const groupData = segmentGroups[segId];
            const sNode = nodesDataMap[groupData.sId], tNode = nodesDataMap[groupData.tId];
            if (!sNode || !tNode) return;
            const startX = sNode.x + sNode.width, endX = tNode.x;
            const inG = createSVGElement("g", { class: "gooey-group-inactive" });
            const actG = createSVGElement("g", { class: "gooey-group-active" });
            inactiveLayer.appendChild(inG);
            activeLayer.appendChild(actG);
            groupData.paths.forEach((pd) => {
                const startY = getPathPortY(groupData.sId, pd.pathId);
                const endY = getPathPortY(groupData.tId, pd.pathId);
                const d = calculatePath(startX, startY, endX, endY);
                const sw = `${PATH_THICKNESS + 2}px`;
                const uniqueKey = pd.pathId + "-" + groupData.sId + "-" + groupData.tId;
                const pInactive = createSVGElement("path", { class: "path-inactive", d, style: `stroke-width: ${sw};` });
                inactivePathElements[uniqueKey] = pInactive;
                inG.appendChild(pInactive);
                const pColor = getGradientColor(config[groupData.colIdx].color, config[groupData.colIdx + 1].color, startX, endX);
                const pActive = createSVGElement("path", { class: "path-active", d, style: `stroke-width: ${sw}; stroke: ${pColor};` });
                activePathElements[uniqueKey] = pActive;
                actG.appendChild(pActive);
            });
        });

        allPaths.forEach((p) => {
            const routeGroup = createSVGElement("g", { class: "route-group", "data-path-id": p.id });
            for (let i = 0; i < p.nodes.length - 1; i++) {
                const sId = p.nodes[i], tId = p.nodes[i + 1];
                if (!nodesDataMap[sId] || !nodesDataMap[tId]) continue;
                const startX = nodesDataMap[sId].x + nodesDataMap[sId].width, endX = nodesDataMap[tId].x;
                const startY = getPathPortY(sId, p.id), endY = getPathPortY(tId, p.id);
                const pathColor = getGradientColor(config[i].color, config[i + 1].color, startX, endX);
                routeGroup.appendChild(createSVGElement("path", {
                    class: "route-segment",
                    d: calculatePath(startX, startY, endX, endY),
                    style: `stroke-width: 14px; stroke: ${pathColor};`
                }));
            }
            hoverBasicLayer.appendChild(routeGroup);
        });

        updateVisuals();
    }

    function getPathPortY(nodeId, pathId) {
        const node = nodesDataMap[nodeId], paths = nodePaths[nodeId];
        if (!node || !paths) return 0;
        const colConfig = config[node.colIdx];
        if (colConfig && colConfig.converge && node.type === "item") {
            const precalcY = convergentPathsY[pathId + "-" + node.colIdx];
            if (precalcY !== undefined) return precalcY;
            return node.groupCenterY;
        }
        const idx = paths.findIndex((p) => p.id === pathId);
        if (idx === -1) return node.y + node.height / 2;
        const totalBlockHeight = paths.length * PATH_THICKNESS;
        return node.y + node.height / 2 - totalBlockHeight / 2 + idx * PATH_THICKNESS + PATH_THICKNESS / 2;
    }

    function getGradientColor(c1, c2, x1, x2) {
        if (!APP_CONFIG.useGradients) return c1;
        const gradientId = `grad-${c1.replace("#", "")}-${c2.replace("#", "")}-${Math.round(x1)}-${Math.round(x2)}`;
        if (!createdGradients.has(gradientId)) {
            const lg = createSVGElement("linearGradient", { id: gradientId, gradientUnits: "userSpaceOnUse", x1, y1: 0, x2, y2: 0 });
            lg.appendChild(createSVGElement("stop", { offset: "0%", "stop-color": c1 }));
            lg.appendChild(createSVGElement("stop", { offset: "100%", "stop-color": c2 }));
            defsLayer.appendChild(lg);
            createdGradients.add(gradientId);
        }
        return `url(#${gradientId})`;
    }

    function handleSelection(colIdx, nodeId) {
        if (VIEW_ONLY) return;
        const isCurrentlySelected = selections[colIdx].includes(nodeId);
        const isGroup = config[colIdx].type === "group";
        if (isSinglePathMode && !isGroup) {
            selections[colIdx] = isCurrentlySelected ? [] : [nodeId];
        } else {
            if (isCurrentlySelected) selections[colIdx] = selections[colIdx].filter((id) => id !== nodeId);
            else selections[colIdx].push(nodeId);
        }
        updateVisuals();
        saveSelectionsToLocalStorage(selections);
        setStateValue("selections", selections);
    }

    function handleNodeHover(nodeId, isEnter) {
        if (VIEW_ONLY) return;
        const nodeInfo = nodesDataMap[nodeId];
        if (nodeInfo && config[nodeInfo.colIdx].converge) return;
        const relatedPaths = allPaths.filter((p) => p.nodes.includes(nodeId)).map((p) => p.id);
        relatedPaths.forEach((pathId) => {
            const group = parentElement.querySelector(`.route-group[data-path-id="${pathId}"]`);
            if (group) isEnter ? group.classList.add("is-node-hovered") : group.classList.remove("is-node-hovered");
        });
    }

    function updateVisuals() {
        const activeColsCount = selections.filter((s) => s.length > 0).length;

        parentElement.querySelectorAll(".sankey-node").forEach((nodeElem) => {
            const id = nodeElem.getAttribute("data-id");
            const colIdx = parseInt(nodeElem.getAttribute("data-col"));
            const rect = nodeElem.querySelector(".node-bar");
            if (selections[colIdx].includes(id)) { rect.style.fill = config[colIdx].color; nodeElem.classList.add("active"); }
            else { rect.style.fill = "var(--inactive-node)"; nodeElem.classList.remove("active"); }
        });

        parentElement.querySelectorAll(".group-item").forEach((itemElem) => {
            const id = itemElem.getAttribute("data-id");
            const colIdx = parseInt(itemElem.getAttribute("data-col"));
            const icon = itemElem.querySelector(".item-icon");
            const text = itemElem.querySelector("text");
            icon.className.baseVal = `item-icon ${isSinglePathMode ? "radio" : "checkbox"}`;
            if (selections[colIdx].includes(id)) {
                icon.style.fill = config[colIdx].color; icon.style.stroke = config[colIdx].color;
                text.style.fontWeight = "700"; text.style.fill = config[colIdx].color;
            } else {
                icon.style.fill = "transparent"; icon.style.stroke = "var(--inactive-node)";
                text.style.fontWeight = "500"; text.style.fill = "var(--text-main)";
            }
        });

        parentElement.querySelectorAll(".group-main-bar").forEach((bar) => {
            const colIdx = parseInt(bar.getAttribute("data-col"));
            bar.style.fill = selections[colIdx].length > 0 ? config[colIdx].color : "var(--inactive-node)";
        });

        parentElement.querySelectorAll(".group-item-bar").forEach((bar) => {
            const colIdx = parseInt(bar.getAttribute("data-col"));
            const id = bar.getAttribute("data-id");
            bar.style.fill = selections[colIdx].includes(id) ? config[colIdx].color : "var(--inactive-node)";
        });

        allPaths.forEach((p) => {
            let isStrictCompatible = true, matchesCount = 0, convergeMatch = false;
            for (let i = 0; i < config.length; i++) {
                const sel = selections[i];
                if (sel.length > 0) {
                    if (config[i].converge) { convergeMatch = true; continue; }
                    if (sel.includes(p.nodes[i])) matchesCount++;
                    else isStrictCompatible = false;
                }
            }
            const selectedRadioCols = selections.filter((s, i) => s.length > 0 && !config[i].converge).length;
            const isFullyActive = isStrictCompatible && (activeColsCount === config.length);
            const isPartiallyActive = isStrictCompatible && selectedRadioCols > 0 && !isFullyActive;
            const isSuggested = APP_CONFIG.showSuggestions && !isFullyActive && !isPartiallyActive && (matchesCount > 0 || convergeMatch);

            const routeGroup = parentElement.querySelector(`.route-group[data-path-id="${p.id}"]`);
            if (routeGroup) {
                routeGroup.classList.remove("is-partial", "is-suggested");
                if (isPartiallyActive) routeGroup.classList.add("is-partial");
                else if (isSuggested) routeGroup.classList.add("is-suggested");
            }

            for (let i = 0; i < p.nodes.length - 1; i++) {
                const key = p.id + "-" + p.nodes[i] + "-" + p.nodes[i + 1];
                const pInactive = inactivePathElements[key], pActive = activePathElements[key];
                if (pInactive && pActive) {
                    if (isFullyActive) { pInactive.style.display = "none"; pActive.style.display = "block"; }
                    else { pInactive.style.display = "block"; pActive.style.display = "none"; }
                }
            }
        });
    }

    function calculatePath(startX, startY, endX, endY) {
        const midX = startX + (endX - startX) * 0.45;
        return `M${startX},${startY} C${midX},${startY} ${midX},${endY} ${endX},${endY}`;
    }

    function createSVGElement(tag, attrs) {
        const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
        for (let key in attrs) el.setAttribute(key, attrs[key]);
        return el;
    }

    // --- CONTROL EXTERNO DESDE STREAMLIT ---
    isGroupConvergeMode = groupCol ? !!groupCol.converge : false;

    init();
}
"""

_sankey_component: ComponentRenderer = v2.component(
    name="sankey_input",
    html=_HTML,
    css=_CSS,
    js=_JS,
    isolate_styles=True
)

def sankey_input(
    config: List[Dict[str, Any]],
    app_config: Optional[Dict[str, Any]] = None,
    initial_selections: Optional[List[List[str]]] = None,
    diagram_options: Optional[Dict[str, Any]] = None,
    presentation: bool = False,
    view_only: bool = False,
    selection_storage_key: Optional[str] = None,
    path_thickness: int = 12,
    normal_node_width: int = 20,
    group_width: int = 170,
    key: Optional[str] = None,
):
    """
    Componente Sankey interactivo para Streamlit.

    Args:
        config: Lista de columnas del diagrama. Cada columna es un dict con:
            - id: identificador de la columna
            - title: título visible
            - type: "radio" (nodos barra) o "group" (panel checkboxes)
            - color: (opcional) color hex; si no se indica usa app_config.columnColors[i]
            - converge: (solo type="group") True para barra única convergente
            - nodes: lista de nodos con id, label y targets (excepto última columna)
        app_config: Opciones visuales (useGradients, showSuggestions, columnColors).
        initial_selections: Selecciones iniciales por columna.
        diagram_options: Opciones de layout (marginTop/Bottom/Left/Right, minNodeGapY, columnSpacing).
        presentation: Si True deshabilita interacción y oculta controles.
        view_only: Si True, renderiza en modo solo visualización (sin listeners).
        selection_storage_key: Clave de localStorage para persistir selections.
        path_thickness: Grosor en px de los caminos (default 12).
        normal_node_width: Ancho en px de nodos tipo radio (default 20).
        group_width: Ancho en px del panel de grupo (default 170).
        key: Clave única del componente Streamlit.

    Returns:
        Objeto con atributo `selections` (lista de listas de ids seleccionados por columna).
    """
    return _sankey_component(
        data={
            "config": config,
            "app_config": app_config or {},
            "initial_selections": initial_selections if st.session_state.get(key) is None else None,
            "diagram_options": diagram_options or {},
            "presentation": presentation,
            "view_only": view_only,
            "selection_storage_key": selection_storage_key,
            "component_key": key,
            "path_thickness": path_thickness,
            "normal_node_width": normal_node_width,
            "group_width": group_width,
        },
        default={"selections": initial_selections or [[] for _ in config]},
        width= "stretch",
        height="content",
        on_selections_change=lambda: None,
        key=key,
    )
