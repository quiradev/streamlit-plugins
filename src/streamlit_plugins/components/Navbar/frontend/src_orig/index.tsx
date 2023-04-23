import React from "react"
import ReactDOM from "react-dom"
import NavBar from "./NavBar"
import { StreamlitProvider } from "streamlit-component-lib-react-hooks";

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
        <NavBar />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
);
