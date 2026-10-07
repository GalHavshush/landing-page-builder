import { useEffect, useRef, useState } from "react";
import { api } from "@/api/client";
import { IconDesktop, IconMobile } from "@/components/icons";
import type { Brief, Tf } from "./model";

type Device = "desktop" | "mobile";
const WIDTH: Record<Device, number> = { desktop: 1280, mobile: 390 };
const HEIGHT: Record<Device, number> = { desktop: 860, mobile: 780 };

/**
 * Live picture of the site the answers so far would produce. The page is laid out at laptop (or
 * phone) width, then scaled down to the column; the last good render stays up while a new one loads.
 */
export function SitePreview({ brief, pageId, T }: { brief: Brief; pageId: string; T: Tf }) {
  type Frame = { id: number; html: string };
  const [shown, setShown] = useState<Frame>(); // what is on screen
  const [incoming, setIncoming] = useState<Frame>(); // the next render, loading out of sight so the swap never flashes
  const counter = useRef(0);
  const [failed, setFailed] = useState(false);
  const [device, setDevice] = useState<Device>("desktop");
  const [box, setBox] = useState(0);
  const holder = useRef<HTMLDivElement>(null);
  const body = JSON.stringify({ brief, page_id: pageId });

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      api<{ html: string }>("/projects/preview-brief", { method: "POST", body: JSON.parse(body), signal: controller.signal }).then(
        (r) => { setFailed(false); setIncoming({ id: ++counter.current, html: r.html }); },
        (e: Error) => e.name !== "AbortError" && setFailed(true),
      );
    }, 450);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [body]);

  useEffect(() => {
    const el = holder.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setBox(el.clientWidth));
    ro.observe(el);
    setBox(el.clientWidth);
    return () => ro.disconnect();
  }, []);

  const w = WIDTH[device], h = HEIGHT[device];
  const scale = box ? Math.min(1, box / w) : 0.3;
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-[12px] font-medium text-ink-500">{T("Live preview")}</span>
        <div role="group" aria-label={T("Preview size")} className="flex gap-0.5 rounded-md bg-ink-100 p-0.5 ring-1 ring-inset ring-ink-200">
          {(["desktop", "mobile"] as const).map((x) => (
            <button key={x} type="button" onClick={() => setDevice(x)} aria-pressed={device === x} aria-label={x === "desktop" ? T("Desktop") : T("Mobile")} title={x === "desktop" ? T("Desktop") : T("Mobile")}
              className={`grid h-6 w-8 place-items-center rounded-[5px] transition ${device === x ? "bg-[var(--surface-raised)] text-ink-900 shadow-[0_1px_2px_rgb(0_0_0/0.18),0_0_0_1px_rgb(127_127_127/0.12)]" : "text-ink-500 hover:text-ink-900"}`}>
              {x === "desktop" ? <IconDesktop size={14} /> : <IconMobile size={14} />}
            </button>
          ))}
        </div>
      </div>
      <div ref={holder} className="rounded-lg bg-ink-100 p-0 ring-1 ring-inset ring-ink-200">
        <div dir="ltr" className="relative mx-auto overflow-hidden rounded-lg bg-white" style={{ width: w * scale, height: h * scale }} aria-hidden>
          {[shown, incoming].map((f, i) => f && (
            <iframe key={f.id} title={T("Live preview")} tabIndex={-1} srcDoc={f.html} sandbox="allow-scripts"
              onLoad={i === 1 ? () => { setShown(f); setIncoming(undefined); } : undefined}
              className={`pointer-events-none absolute left-0 top-0 origin-top-left border-0 ${i === 1 ? "invisible" : ""}`}
              style={{ width: w, height: h, transform: `scale(${scale})` }} />
          ))}
          {!shown && !incoming && (
            <p className="grid h-full place-items-center text-[12px] text-ink-500">{failed ? T("Preview unavailable") : T("Loading…")}</p>
          )}
        </div>
      </div>
      {failed && shown && <p className="mt-1.5 text-[12px] text-ink-500">{T("Preview unavailable")}</p>}
    </div>
  );
}
