import { useEffect, useRef, useState } from "react";
import { api } from "@/api/client";
import type { SiteDocument } from "@/api/types";
import { useEditor } from "./store";

interface PreviewResponse {
  html: string;
  issues: { level: string; message: string; where: string }[];
}

/** Fetches rendered HTML for the page being edited (debounced, latest request wins). */
export function usePreviewHtml(projectId: number, doc: SiteDocument, pageId: string, lang: string) {
  const [state, setState] = useState<{ html?: string; error?: string }>({});
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await api<PreviewResponse>(`/projects/${projectId}/preview`, {
          method: "POST",
          body: { doc, page_id: pageId, lang },
          signal: controller.signal,
        });
        setState({ html: res.html });
      } catch (e) {
        if ((e as Error).name !== "AbortError") setState((s) => ({ ...s, error: (e as Error).message }));
      }
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [projectId, doc, pageId, lang]);
  return state;
}

/**
 * Two stacked iframes: a new render loads in the hidden one and is swapped in when ready,
 * so edits don't flash white, and the scroll position carries over.
 * sandbox="allow-scripts" (no allow-same-origin): the preview can run its tiny selection script
 * but cannot touch the editor's cookies or DOM.
 */
export function Preview({ html }: { html: string | undefined }) {
  const frames = [useRef<HTMLIFrameElement>(null), useRef<HTMLIFrameElement>(null)];
  const [active, setActive] = useState(0);
  const activeRef = useRef(0);
  const scrollY = useRef(0);
  const selectedId = useEditor((s) => s.selectedId);
  const selectSection = useEditor((s) => s.selectSection);
  const device = useEditor((s) => s.device);

  useEffect(() => {
    if (html === undefined) return;
    const next = 1 - activeRef.current;
    const frame = frames[next].current;
    if (frame) frame.srcdoc = html;
  }, [html]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      const idx = frames.findIndex((f) => f.current?.contentWindow === e.source);
      if (idx === -1) return; // not from one of our preview frames
      const msg = e.data ?? {};
      if (msg.type === "preview-ready") {
        frames[idx].current?.contentWindow?.postMessage({ type: "restore-scroll", y: scrollY.current }, "*");
        frames[idx].current?.contentWindow?.postMessage({ type: "select", id: useEditor.getState().selectedId }, "*");
        activeRef.current = idx;
        setActive(idx);
      } else if (msg.type === "scroll" && idx === activeRef.current) {
        scrollY.current = msg.y;
      } else if (msg.type === "section-click" && idx === activeRef.current) {
        selectSection(msg.id);
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [selectSection]); // eslint-disable-line react-hooks/exhaustive-deps

  // tell the visible frame which section is selected (e.g. picked from the section list)
  useEffect(() => {
    frames[activeRef.current].current?.contentWindow?.postMessage(
      { type: "select", id: selectedId, scroll: true },
      "*",
    );
  }, [selectedId, active]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex h-full justify-center overflow-hidden bg-slate-200 p-4">
      <div
        className={`relative h-full overflow-hidden bg-white shadow-lg ring-1 ring-slate-300 transition-[width] duration-200 ${
          device === "mobile" ? "w-[390px] rounded-2xl" : "w-full rounded-lg"
        }`}
      >
        {[0, 1].map((i) => (
          <iframe
            key={i}
            ref={frames[i]}
            title={`Preview ${i}`}
            sandbox="allow-scripts"
            className={`absolute inset-0 h-full w-full border-0 ${active === i ? "visible" : "invisible"}`}
          />
        ))}
      </div>
    </div>
  );
}
