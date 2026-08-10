/**
 * App root.
 * Wires up the Redux store, router, and session bootstrap.
 */

import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { store } from "@/store";
import { AppRoutes } from "@/routes/AppRoutes";
import { AppBootstrap } from "@/components/AppBootstrap";

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppBootstrap />
        <AppRoutes />
      </BrowserRouter>
    </Provider>
  );
}
