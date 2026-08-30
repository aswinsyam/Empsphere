/**
 * Application root component.
 *
 * Bootstraps the entire frontend by composing:
 * - Redux store via `Provider`
 * - Client-side routing via `BrowserRouter`
 * - Global toast notifications via `ToastProvider`
 * - Session restoration via `AppBootstrap`
 * - Route definitions via `AppRoutes`
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
