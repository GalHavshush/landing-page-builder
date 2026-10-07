import { useEffect, useRef, useState } from "react";
import { IconClose, IconDesktop, IconMobile } from "@/components/icons";
import { t } from "@/i18n";

type Target = { page: string | null; lang: string | null };
type Device = "desktop" | "mobile";

/**
 * Full-screen, click-through preview of the finished site with a desktop/mobile switch.
 * `load` returns the page's HTML; menu and page links in the site ask for another page via
 * postMessage (the frame is sandboxed, so it can run the site's scripts but touch nothing else).
 */
export function LivePreview({
  title, load, onClose,
}: {
  title: string;
  load: (target: Target, signal: AbortSignal) => Promise<string>;
  onClose: () => void;
}) {
  const [target, setTarget] = useState<Target>({ page: null, lang: null });
  const [html, setHtml] = useState<string>();
  const [error, setError] = useState<string>();
  const [device, setDevice] = useState<Device>("desktop");
  const frame = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    setError(undefined);
    load(target, controller.signal).then(setHtml, (e: Error) => e.name !== "AbortError" && setError(e.message));
    return () => controller.abort();
  }, [target]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      if (e.source !== frame.current?.contentWindow || e.data?.type !== "navigate") return;
      setTarget({ page: String(e.data.page), lang: String(e.data.lang) });
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("message", onMessage);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("message", onMessage);
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  return (
    <div role="dialog" aria-modal="true" aria-label={t("Preview of {name}", { name: title })} className="fixed inset-0 z-50 flex flex-col bg-ink-100">
      <header className="grid h-11 shrink-0 grid-cols-[1fr_auto_1fr] items-center border-b border-ink-200 bg-white px-3">
        <h2 className="truncate text-[13px] font-semibold tracking-tight">{title}</h2>
        <div role="group" aria-label={t("Preview size")} className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200">
          {(["desktop", "mobile"] as const).map((d) => (
            <button key={d} type="button" onClick={() => setDevice(d)} aria-pressed={device === d} aria-label={d === "desktop" ? t("Desktop") : t("Mobile")} title={d === "desktop" ? t("Desktop") : t("Mobile")}
              className={`grid h-6 w-8 place-items-center rounded-[5px] transition ${device === d ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-500 hover:text-ink-900"}`}>
              {d === "desktop" ? <IconDesktop size={14} /> : <IconMobile size={14} />}
            </button>
          ))}
        </div>
        <div className="flex justify-end">
          <button type="button" autoFocus aria-label={t("Close preview")} title={`${t("Close preview")}  Esc`} onClick={onClose}
            className="grid h-7 w-7 place-items-center rounded-md text-ink-600 transition hover:bg-ink-100 hover:text-ink-900"><IconClose size={15} /></button>
        </div>
      </header>
      <div className="flex min-h-0 flex-1 justify-center p-4">
        <div className={`relative h-full overflow-hidden bg-white shadow-[0_0_0_1px_rgb(127_127_127/0.2),0_12px_32px_-12px_rgb(0_0_0/0.35)] transition-[width,border-radius] duration-300 ease-[var(--ease-out-quart)] ${device === "mobile" ? "w-[390px] rounded-[22px]" : "w-full rounded-lg"}`}>
          <iframe ref={frame} title={t("Preview of {name}", { name: title })} srcDoc={html} sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox" className="h-full w-full border-0" />
          {!html && !error && <p className="absolute inset-0 grid place-items-center text-[13px] text-ink-500">{t("Loading…")}</p>}
          {error && <p role="alert" className="absolute inset-x-4 top-4 rounded-md bg-red-600 px-3 py-2 text-sm text-white shadow">{t("Preview failed: {error}", { error: t(error) })}</p>}
        </div>
      </div>
    </div>
  );
}
