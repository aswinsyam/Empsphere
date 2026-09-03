/**
 * Application entry point.
 *
 * Mounts the React app into the DOM using React 18's `createRoot` API.
 * Wraps the app in `React.StrictMode` for development-time checks
 * and imports the global stylesheet.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/globals.css";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
