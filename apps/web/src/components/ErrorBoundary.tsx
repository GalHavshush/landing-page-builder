import { Component, type ErrorInfo, type ReactNode } from "react";

/** Last line of defence: a crash in one screen shows a message instead of a blank page. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("UI crashed:", error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-3 px-4">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="text-sm text-ink-600">
          Your saved work is safe. Reload the page to continue. If it keeps happening, tell us what you were doing.
        </p>
        <button className="self-start rounded-md bg-ink-900 px-3 py-1.5 text-[13px] font-medium text-white" onClick={() => window.location.reload()}>
          Reload
        </button>
      </main>
    );
  }
}
