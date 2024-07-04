import React from "react";
import ReactDOM from "react-dom";
import SpeechTranscriber from "./SpeechTranscriber";
import StreamlitProvider from "./Provider";

ReactDOM.render(
  <React.StrictMode>
    <StreamlitProvider>
        <SpeechTranscriber />
    </StreamlitProvider>
  </React.StrictMode>,
  document.getElementById("root")
);