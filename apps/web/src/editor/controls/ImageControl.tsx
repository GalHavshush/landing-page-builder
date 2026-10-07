import { useRef, useState } from "react";
import { useAssets, useDeleteAsset, useStockSearch, useUploadAsset } from "@/api/hooks";
import type { Asset } from "@/api/types";
import { IconClose } from "@/components/icons";
import { Button } from "@/components/ui";
import { useEditor } from "../store";
import { FieldShell, type ControlProps } from "./basic";
import { StockPanel } from "./StockPanel";

export interface ImageValue {
  asset: string;
  alt: string;
  focus: { x: number; y: number };
}

/**
 * Click or drag on the picture to say which part matters. When the image is cropped (a wide hero, a
 * square card, a phone screen) that point stays in view.
 */
function FocusPicker({ src, focus, onChange }: { src: string; focus: { x: number; y: number }; onChange: (f: { x: number; y: number }) => void }) {
  const set = (e: React.PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const clamp = (n: number) => Math.round(Math.min(100, Math.max(0, n)));
    onChange({ x: clamp(((e.clientX - r.left) / r.width) * 100), y: clamp(((e.clientY - r.top) / r.height) * 100) });
  };
  return (
    <div>
      <div className="field-label mb-1">Focus point</div>
      <div
        role="slider" aria-label="Focus point" aria-valuetext={`${focus.x}% across, ${focus.y}% down`} tabIndex={0}
        className="relative cursor-crosshair touch-none select-none overflow-hidden rounded-md ring-1 ring-ink-200"
        onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); set(e); }}
        onPointerMove={(e) => e.buttons === 1 && set(e)}
        onKeyDown={(e) => {
          const step = e.shiftKey ? 10 : 2;
          const d = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
          if (!d) return;
          e.preventDefault();
          onChange({ x: Math.min(100, Math.max(0, focus.x + d[0])), y: Math.min(100, Math.max(0, focus.y + d[1])) });
        }}
      >
        <img src={src} alt="" draggable={false} className="block w-full" />
        <span aria-hidden className="pointer-events-none absolute h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow-[0_0_0_1.5px_rgb(0_0_0/0.55)]"
          style={{ left: `${focus.x}%`, top: `${focus.y}%` }}>
          <span className="absolute left-1/2 top-1/2 h-1 w-1 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white" />
        </span>
      </div>
      <p className="mt-1.5 text-[12px] leading-snug text-ink-500">Cropping on cards, heroes and phones keeps this point in view.</p>
    </div>
  );
}

/** Image field: shows the chosen image, lets you pick/upload another, and edit its alt text. */
export function ImageControl({
  label, value, onChange, hideAlt,
}: ControlProps<ImageValue | null> & { hideAlt?: boolean }) {
  const projectId = useEditor((s) => s.projectId)!;
  const assets = useAssets(projectId);
  const dialog = useRef<HTMLDialogElement>(null);
  const current = assets.data?.find((a) => a.id === value?.asset);

  return (
    <FieldShell label={label}>
      <div className="mt-1 space-y-2">
        {value && (
          <div className="flex items-center gap-2 rounded-md border border-ink-200 p-1.5">
            {current ? (
              <img src={current.thumb_url} alt="" className="h-14 w-14 rounded object-cover" />
            ) : (
              <div className="grid h-14 w-14 place-items-center rounded bg-ink-100 text-xs text-ink-500">?</div>
            )}
            <div className="min-w-0 flex-1 truncate text-xs text-ink-500">{current?.filename ?? "Image missing from library"}</div>
            <button type="button" onClick={() => onChange(null)} className="px-1 text-xs text-ink-500 hover:text-red-600" aria-label={`Remove ${label}`}>
              Remove
            </button>
          </div>
        )}
        <Button type="button" variant="ghost" className="w-full" onClick={() => dialog.current?.showModal()}>
          {value ? "Change image" : "Choose image"}
        </Button>
        {value && !hideAlt && current && (
          <FocusPicker src={current.thumb_url} focus={value.focus ?? { x: 50, y: 50 }} onChange={(focus) => onChange({ ...value, focus })} />
        )}
        {value && !hideAlt && (
          <div>
            <label className="block text-xs text-ink-500" htmlFor={`${label}-alt`}>
              Description for screen readers (alt text)
            </label>
            <input id={`${label}-alt`} value={value.alt} placeholder="e.g. Fresh loaves on a wooden table"
              onChange={(e) => onChange({ ...value, alt: e.target.value }, true)}
              className="mt-1 block w-full rounded-md border border-ink-300 px-2.5 py-1.5 text-sm" />
          </div>
        )}
      </div>
      <AssetPicker
        dialogRef={dialog}
        projectId={projectId}
        selected={value?.asset}
        onPick={(a) => {
          // keep the alt text if the user is just swapping the picture
          onChange({ asset: a.id, alt: value?.alt || a.alt_default, focus: value?.focus ?? { x: 50, y: 50 } });
          dialog.current?.close();
        }}
      />
    </FieldShell>
  );
}

export function AssetPicker({
  dialogRef, projectId, selected, onPick,
}: {
  dialogRef: React.RefObject<HTMLDialogElement | null>;
  projectId: number;
  selected?: string;
  onPick: (a: Asset) => void;
}) {
  const assets = useAssets(projectId);
  const upload = useUploadAsset(projectId);
  const remove = useDeleteAsset(projectId);
  const [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const [tab, setTab] = useState<"mine" | "stock">("mine");
  const stockOn = useStockSearch(projectId, "").data?.enabled ?? false;

  const send = (files: FileList | File[]) => {
    Array.from(files).forEach((f) => upload.mutate(f, { onSuccess: (a) => files.length === 1 && onPick(a) }));
  };
  const error = (upload.error ?? remove.error)?.message;

  return (
    <dialog ref={dialogRef} className="m-auto w-[min(44rem,94vw)] rounded-2xl bg-white p-0"
      onClick={(e) => e.target === dialogRef.current && dialogRef.current?.close()}>
      <div className="p-5" onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); send(e.dataTransfer.files); }}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold tracking-tight">Images</h2>
          <div className="flex items-center gap-2">
            <input ref={input} type="file" accept="image/jpeg,image/png,image/webp" multiple hidden
              onChange={(e) => e.target.files && send(e.target.files)} />
            <Button type="button" onClick={() => input.current?.click()} disabled={upload.isPending}>
              {upload.isPending ? "Uploading…" : "Upload image"}
            </Button>
            <button aria-label="Close" className="grid h-7 w-7 place-items-center rounded-md text-ink-500 hover:bg-ink-100 hover:text-ink-900" onClick={() => dialogRef.current?.close()}><IconClose size={15} /></button>
          </div>
        </div>
        {stockOn && (
          <div role="tablist" aria-label="Image source" className="mb-3 flex gap-4 border-b border-ink-200">
            {([["mine", "My images"], ["stock", "Stock photos"]] as const).map(([k, l]) => (
              <button key={k} role="tab" type="button" aria-selected={tab === k} onClick={() => setTab(k)}
                className={`-mb-px border-b-[1.5px] py-2 text-[13px] font-medium transition ${tab === k ? "border-ink-900 text-ink-900" : "border-transparent text-ink-500 hover:text-ink-800"}`}>{l}</button>
            ))}
          </div>
        )}
        {error && <p role="alert" className="mb-3 text-sm text-red-600">{error}</p>}
        {stockOn && tab === "stock" ? <StockPanel projectId={projectId} onPick={onPick} /> : (
        <div className={`rounded-lg border-2 border-dashed p-3 ${dragging ? "border-accent-500 bg-accent-50" : "border-ink-200"}`}>
          {assets.data?.length === 0 && <p className="py-8 text-center text-sm text-ink-500">Drop images here or use “Upload image”. JPEG, PNG or WebP, up to 10 MB.</p>}
          <ul className="grid grid-cols-3 gap-3 sm:grid-cols-4">
            {assets.data?.map((a) => (
              <li key={a.id} className="group relative">
                <button type="button" onClick={() => onPick(a)} aria-label={`Use ${a.filename}`}
                  className={`block aspect-square w-full overflow-hidden rounded-md ring-2 ${a.id === selected ? "ring-accent-500" : "ring-transparent hover:ring-accent-300"}`}>
                  <img src={a.thumb_url} alt={a.alt_default} className="h-full w-full object-cover" />
                </button>
                <button type="button" aria-label={`Delete ${a.filename}`} title="Delete from library"
                  onClick={() => window.confirm("Delete this image from the library?") && remove.mutate(a.id)}
                  className="absolute right-1 top-1 grid h-5 w-5 place-items-center rounded bg-white text-ink-600 opacity-0 shadow-sm ring-1 ring-ink-200 hover:bg-red-600 hover:text-white group-hover:opacity-100 focus:opacity-100"><IconClose size={12} /></button>
              </li>
            ))}
          </ul>
        </div>
        )}
      </div>
    </dialog>
  );
}
