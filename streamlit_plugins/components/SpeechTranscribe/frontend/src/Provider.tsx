import React, { useEffect, useContext, useState } from "react";
import { Streamlit, RenderData, Theme } from "streamlit-component-lib";

interface ErrorBoundaryProps {
  children: React.ReactNode;
}
interface ErrorBoundaryState {
  error: Error | undefined;
}

/**
 * Shows errors thrown from child components.
 */
class ErrorBoundary extends React.PureComponent<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: undefined };
  }

  static getDerivedStateFromError(error: Error) {
    // Update state so the next render will show the fallback UI.
    return { error };
  }

  render() {
    if (this.state.error != null) {
      return (
        <div>
          <h1>Component Error</h1>
          <span>{this.state.error.message}</span>
        </div>
      );
    }

    return this.props.children;
  }
}


/** Post a message to the Streamlit app. */
const sendBackMsg = (type: string, data?: any): void => {
  window.parent.postMessage(
    {
      isStreamlitMessage: true,
      type: type,
      ...data
    },
    "*"
  );
};

/**
 * Returns `RenderData` received from Streamlit after the first render event received.
 */
const useNullableRenderData = (): RenderData | undefined => {
  const [renderData, setRenderData] = useState<RenderData>();

  useEffect(() => {
    const onRenderEvent = (event: Event): void => {
      const renderEvent = event as CustomEvent<RenderData>;
      setRenderData(renderEvent.detail);
    };

    let overrideEvent = false;
    let streamlitOnMessageEvent: Function | null;

    const onMessageEvent = (event: MessageEvent): void => {
      // TODO: Borrar del document: head, los styles que contengan el mismo texto consecutivo
      let theme: Theme | undefined = event.data["theme"];
      if (theme) {
        let regex = /:root \{[^}]+\}\s+body \{[^}]+\}/;
        const themeStyles: HTMLStyleElement[] = [];
        Array.from(document.head
          .querySelectorAll("style"))
          .forEach((style) => {
            // console.log(el);
            const css = style.textContent;
            if (css){
                const match = regex.exec(css);

                if (match) {
                  themeStyles.push(style);
                }
            }

          });
          themeStyles.slice(0,-1).forEach(style => {
            document.head.removeChild(style);
          });
      }
      // Se propaga el ultimo
      if (streamlitOnMessageEvent) streamlitOnMessageEvent(event);
    };

    const setOverrideComponentReady = (): void => {
      if (!overrideEvent) {
        // Register for message events if we haven't already
        streamlitOnMessageEvent = window.onmessage || (() => {});
        window.addEventListener("message", onMessageEvent);
        overrideEvent = true;
      }
      sendBackMsg("streamlit:componentReady", {
        apiVersion: Streamlit.API_VERSION
      });
    };
    // Set up event listeners, and signal to Streamlit that we're ready.
    // We won't render the component until we receive the first RENDER_EVENT.
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRenderEvent);
    Streamlit.setComponentReady();
    setOverrideComponentReady();

    const cleanup = () => {
      Streamlit.events.removeEventListener(
        Streamlit.RENDER_EVENT,
        onRenderEvent
      );
    };
    return cleanup;
  }, []);

  return renderData;
};

const renderDataContext = React.createContext<RenderData | undefined>(
  undefined
);

/**
 * Returns `RenderData` received from Streamlit.
 */
export const useRenderData = (): RenderData => {
  const contextValue = useContext(renderDataContext);
  if (contextValue == null) {
    throw new Error(
      "useRenderData() must be used inside <StreamlitProvider />"
    );
  }

  return contextValue;
};

/**
 * Wrapper for React-hooks-based Streamlit components.
 *
 * Bootstraps the communication interface between Streamlit and the component.
 */
interface StreamlitProviderProps {
  children: React.ReactNode;
}
const StreamlitProvider: React.VFC<StreamlitProviderProps> = (props) => {
  const renderData = useNullableRenderData();

  useEffect(() => {
    Streamlit.setFrameHeight();
  });

  // Don't render until we've gotten our first data from Streamlit.
  if (renderData == null) {
    return null;
  }

  return (
    <ErrorBoundary>
      <renderDataContext.Provider value={renderData}>
        {props.children}
      </renderDataContext.Provider>
    </ErrorBoundary>
  );
};

export default StreamlitProvider;