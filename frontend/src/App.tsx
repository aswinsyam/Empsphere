/**
 * App root.
 * Wires up the Redux store, router, and session bootstrap.
 */

import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { store } from "@/store";
import { AppRoutes } from "@/routes/AppRoutes";
import { AppBootstrap } from "@/components/AppBootstrap";
import { ToastProvider } from "@/components/common/ToastProvider";

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <ToastProvider>
          <AppBootstrap />
          <AppRoutes />
        </ToastProvider>
      </BrowserRouter>
    </Provider>
  );
}
