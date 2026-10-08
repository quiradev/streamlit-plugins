/** @jsxImportSource react */
import React from "react";
import { createRoot, Root } from "react-dom/client";

import {
  CleanupFunction,
  FrontendRenderer,
  FrontendRendererArgs,
  FrontendState,
} from "@streamlit/component-v2-lib";

// Paquetes npm: fuente Material Symbols y estilos Bootstrap
import "@fontsource/material-symbols-rounded";
import "bootstrap/dist/css/bootstrap.min.css";

import NativeNavBarV2, { NativeNavBarV2Props } from "./NativeNavBarV2";

// ---------------------------------------------------------------------------
// Caches keyed by parentElement (same pattern as FileUploaderRenderer example)
// ---------------------------------------------------------------------------

const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getRenderRoot(parentElement: FrontendRendererArgs["parentElement"]) {
  const rootNode = parentElement.getRootNode();

  if (rootNode instanceof ShadowRoot) {
    return rootNode.querySelector(".react-root");
  }

  return parentElement.querySelector(".react-root");
}

function isNavBarData(
  data: Record<string, unknown>,
): data is Record<string, unknown> & NativeNavBarV2Props {
  return (
    Array.isArray(data.menu_definition) &&
    typeof data.position_mode === "string" &&
    ["top", "under", "side", "static", "hidden"].includes(data.position_mode) &&
    typeof data.is_sticky === "boolean" &&
    typeof data.is_navigation === "boolean" &&
    typeof data.default_page_selected_id === "string"
  );
}

// ---------------------------------------------------------------------------
// FrontendRenderer entry point (Streamlit component v2)
// ---------------------------------------------------------------------------

const NavBarRenderer: FrontendRenderer<
  FrontendState,
  Record<string, unknown>
> = (args): CleanupFunction => {
  const { data, parentElement, setStateValue } = args;

  if (!isNavBarData(data)) {
    throw new Error("Navbar V2 received invalid component data");
  }

  const rootElement = getRenderRoot(parentElement);
  if (!rootElement) {
    throw new Error("Unexpected: React root element not found");
  }

  let reactRoot = reactRoots.get(parentElement);
  if (!reactRoot) {
    reactRoot = createRoot(rootElement as HTMLElement);
    reactRoots.set(parentElement, reactRoot);
  }

  const props = data as NativeNavBarV2Props;
  const theme = data.theme as React.ComponentProps<typeof NativeNavBarV2>["theme"];

  reactRoot.render(
    <React.StrictMode>
      <NativeNavBarV2
        args={props}
        theme={theme}
        setStateValue={setStateValue}
      />
    </React.StrictMode>
  );

  return () => {
    const root = reactRoots.get(parentElement);
    if (root) {
      root.unmount();
      reactRoots.delete(parentElement);
    }
  };
};

export default NavBarRenderer;
