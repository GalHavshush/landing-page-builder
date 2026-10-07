import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { queryClient } from "./api/queryClient";
import App from "./App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./index.css";
import { applyLang, useUiLang } from "./i18n";
import { initTheme } from "./theme";

initTheme();
applyLang();

/** Remounting on a language change re-renders every string and keeps the document direction in step. */
function Root() {
  const lang = useUiLang();
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <App key={lang} />
        </ErrorBoundary>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Root />
  </StrictMode>,
);
