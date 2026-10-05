import { useRef, useState } from "react";
import { useAssets, useDeleteAsset, useUploadAsset } from "@/api/hooks";
import type { Asset } from "@/api/types";
import { Button } from "@/components/ui";
import { useEditor } from "../store";
import { FieldShell, type ControlProps } from "./basic";

export interface ImageValue {
  asset: string;
  alt: string;
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
          <div className="flex items-center gap-2 rounded-md border border-slate-200 p-1.5">
            {current ? (
              <img src={current.thumb_url} alt="" className="h-14 w-14 rounded object-cover" />
            ) : (
              <div className="grid h-14 w-14 place-items-center rounded bg-slate-100 text-xs text-slate-400">?</div>
            )}
            <div className="min-w-0 flex-1 truncate text-xs text-slate-500">{current?.filename ?? "Image missing from library"}</div>
            <button type="button" onClick={() => onChange(null)} className="px-1 text-xs text-slate-500 hover:text-red-600" aria-label={`Remove ${label}`}>
              Remove
            </button>
          </div>
        )}
        <Button type="button" variant="ghost" className="w-full" onClick={() => dialog.current?.showModal()}>
          {value ? "Change image" : "Choose image"}
        </Button>
        {value && !hideAlt && (
          <div>
            <label className="block text-xs text-slate-500" htmlFor={`${label}-alt`}>
              Description for screen readers (alt text)
            </label>
            <input id={`${label}-alt`} value={value.alt} placeholder="e.g. Fresh loaves on a wooden table"
              onChange={(e) => onChange({ ...value, alt: e.target.value }, true)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm" />
          </div>
        )}
      </div>
      <AssetPicker
        dialogRef={dialog}
        projectId={projectId}
        selected={value?.asset}
        onPick={(a) => {
          // keep the alt text if the user is just swapping the picture
          onChange({ asset: a.id, alt: value?.alt || a.alt_default });
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

  const send = (files: FileList | File[]) => {
    Array.from(files).forEach((f) => upload.mutate(f, { onSuccess: (a) => files.length === 1 && onPick(a) }));
  };
  const error = (upload.error ?? remove.error)?.message;

  return (
    <dialog ref={dialogRef} className="m-auto w-[min(44rem,94vw)] rounded-xl p-0 shadow-2xl backdrop:bg-slate-900/40"
      onClick={(e) => e.target === dialogRef.current && dialogRef.current?.close()}>
      <div className="p-5" onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); send(e.dataTransfer.files); }}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Images</h2>
          <div className="flex items-center gap-2">
            <input ref={input} type="file" accept="image/jpeg,image/png,image/webp" multiple hidden
              onChange={(e) => e.target.files && send(e.target.files)} />
            <Button type="button" onClick={() => input.current?.click()} disabled={upload.isPending}>
              {upload.isPending ? "Uploading…" : "Upload image"}
            </Button>
            <button aria-label="Close" className="px-1 text-slate-500 hover:text-slate-900" onClick={() => dialogRef.current?.close()}>✕</button>
          </div>
        </div>
        {error && <p role="alert" className="mb-3 text-sm text-red-600">{error}</p>}
        <div className={`rounded-lg border-2 border-dashed p-3 ${dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-200"}`}>
          {assets.data?.length === 0 && <p className="py-8 text-center text-sm text-slate-500">Drop images here or use “Upload image”. JPEG, PNG or WebP, up to 10 MB.</p>}
          <ul className="grid grid-cols-3 gap-3 sm:grid-cols-4">
            {assets.data?.map((a) => (
              <li key={a.id} className="group relative">
                <button type="button" onClick={() => onPick(a)} aria-label={`Use ${a.filename}`}
                  className={`block aspect-square w-full overflow-hidden rounded-md ring-2 ${a.id === selected ? "ring-indigo-500" : "ring-transparent hover:ring-indigo-300"}`}>
                  <img src={a.thumb_url} alt={a.alt_default} className="h-full w-full object-cover" />
                </button>
                <button type="button" aria-label={`Delete ${a.filename}`} title="Delete from library"
                  onClick={() => window.confirm("Delete this image from the library?") && remove.mutate(a.id)}
                  className="absolute right-1 top-1 rounded bg-white/90 px-1.5 text-xs text-slate-600 opacity-0 shadow hover:text-red-600 group-hover:opacity-100 focus:opacity-100">✕</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </dialog>
  );
}
