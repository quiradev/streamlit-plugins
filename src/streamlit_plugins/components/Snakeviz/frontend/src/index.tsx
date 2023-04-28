import React from "react";
import ReactDOM from "react-dom";
import NavBar from "./NavBar";
import StreamlitProvider from "./NavBarProvider";

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
        <NavBar />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
);