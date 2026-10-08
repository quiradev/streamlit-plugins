import React from "react";
import ReactDOM from "react-dom";
// import NavBar from "./NavBar";
import NativeNavBar from "./NativeNavBar";
// import StreamlitProvider from "./NavBarProvider";

// ReactDOM.render(
//   <React.StrictMode>
//     <StreamlitProvider>
//         <NavBar />
//     </StreamlitProvider>
//   </React.StrictMode>,
//   document.getElementById("root")
// );

ReactDOM.render(
  <React.StrictMode>
    <NativeNavBar />
  </React.StrictMode>,
  document.getElementById("root")
);