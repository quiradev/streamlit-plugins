import React from "react";
import ReactDOM from "react-dom";
import Snakeviz from "./Snakeviz";
import StreamlitProvider from "./Provider";

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
        <Snakeviz />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
);