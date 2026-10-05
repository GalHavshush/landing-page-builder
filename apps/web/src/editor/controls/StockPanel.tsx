import { useState, type FormEvent } from "react";
import { useImportStock, useStockSearch, type StockPhoto } from "@/api/hooks";
import type { Asset } from "@/api/types";
import { Button } from "@/components/ui";

/** Search free stock photos; picking one imports it into the library like an upload. */
export function StockPanel({ projectId, onPick }: { projectId: number; onPick: (a: Asset) => void }) {
  const [text, setText] = useState("");
  const [q, setQ] = useState("");
  const search = useStockSearch(projectId, q);
  const importPhoto = useImportStock(projectId);
  const [busy, setBusy] = useState<string | null>(null);

  const submit = (e: FormEvent) => { e.preventDefault(); setQ(text.trim()); };
  const choose = (p: StockPhoto) => {
    setBusy(p.id);
    importPhoto.mutate(p.id, { onSuccess: onPick, onSettled: () => setBusy(null) });
  };

  return (
    <div>
      <form onSubmit={submit} className="mb-3 flex gap-2">
        <input aria-label="Search stock photos" value={text} onChange={(e) => setText(e.target.value)}
          placeholder="Search free photos, e.g. bakery, plumber, garden" className="field-input flex-1" />
        <Button type="submit">Search</Button>
      </form>
      {importPhoto.error && <p role="alert" className="mb-2 text-sm text-red-600">{importPhoto.error.message}</p>}
      {search.error && <p role="alert" className="mb-2 text-sm text-red-600">{search.error.message}</p>}
      {search.data && search.data.results.length === 0 && q && <p className="py-6 text-center text-sm text-ink-500">No photos found. Try a simpler word.</p>}
      <ul className="grid grid-cols-3 gap-3 sm:grid-cols-4">
        {search.data?.results.map((p) => (
          <li key={p.id}>
            <button type="button" disabled={busy !== null} onClick={() => choose(p)} aria-label={`Use photo: ${p.alt || p.credit}`}
              className="block aspect-square w-full overflow-hidden rounded-md ring-2 ring-transparent hover:ring-accent-300 disabled:opacity-60">
              <img src={p.thumb_url} alt={p.alt} loading="lazy" className="h-full w-full object-cover" />
            </button>
            <div className="mt-0.5 truncate text-[10.5px] text-ink-500">{busy === p.id ? "Adding…" : p.credit}</div>
          </li>
        ))}
      </ul>
      {search.data?.results.length ? <p className="mt-3 text-[11px] text-ink-500">Photos are free to use from Pexels. Choosing one copies it into your library.</p> : null}
    </div>
  );
}
