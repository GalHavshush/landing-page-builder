import { useState, type FormEvent } from "react";
import { ApiError } from "@/api/client";
import { usePostMutations, usePosts } from "@/api/hooks";
import { Button } from "@/components/ui";
import { slugify } from "../commands";
import { useEditor } from "../store";

const STATUS_STYLE: Record<string, string> = {
  published: "bg-emerald-50 text-emerald-700",
  draft: "bg-slate-100 text-slate-600",
};

/** Left rail in Blog view: every post of the site, plus "new post". */
export function BlogList() {
  const projectId = useEditor((s) => s.projectId)!;
  const doc = useEditor((s) => s.doc)!;
  const postId = useEditor((s) => s.postId);
  const openPost = useEditor((s) => s.openPost);
  const posts = usePosts(projectId);
  const { create } = usePostMutations(projectId);
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [lang, setLang] = useState(doc.site.default_language);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const base = slugify(title) || "post";
    setError(null);
    // a clash on the URL name just means "try the next free one"
    for (let n = 1; n <= 20; n++) {
      try {
        const post = await create.mutateAsync({ lang, title: title.trim(), slug: n === 1 ? base : `${base}-${n}`, excerpt: "", body_md: "", status: "draft" });
        setTitle("");
        setAdding(false);
        openPost(post.id);
        return;
      } catch (err) {
        if (!(err instanceof ApiError && err.status === 409)) return setError((err as Error).message);
      }
    }
  };

  return (
    <aside className="flex min-h-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex-1 overflow-y-auto p-3">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Posts</h2>
          <button className="text-xs text-indigo-600 hover:underline" onClick={() => setAdding(!adding)}>
            {adding ? "Cancel" : "+ New post"}
          </button>
        </div>
        {adding && (
          <form onSubmit={submit} className="mb-3 space-y-2 rounded-md border border-slate-200 p-2">
            <input autoFocus required aria-label="Post title" value={title} onChange={(e) => setTitle(e.target.value)}
              placeholder="Post title" className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm" />
            {doc.site.languages.length > 1 && (
              <select aria-label="Post language" value={lang} onChange={(e) => setLang(e.target.value)}
                className="w-full rounded-md border border-slate-300 bg-white px-2 py-1 text-sm">
                {doc.site.languages.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            )}
            {error && <p role="alert" className="text-xs text-red-600">{error}</p>}
            <Button type="submit" className="w-full" disabled={create.isPending}>Create draft</Button>
          </form>
        )}
        <ul className="space-y-1">
          {posts.data?.map((p) => (
            <li key={p.id}>
              <button onClick={() => openPost(p.id)}
                className={`w-full rounded-md border px-2.5 py-2 text-left ${p.id === postId ? "border-indigo-400 bg-indigo-50" : "border-slate-200 hover:border-slate-300"}`}>
                <div className="truncate text-sm font-medium">{p.title}</div>
                <div className="mt-0.5 flex items-center gap-1.5 text-xs">
                  <span className={`rounded px-1.5 py-0.5 ${STATUS_STYLE[p.status]}`}>{p.status}</span>
                  {doc.site.languages.length > 1 && <span className="text-slate-400">{p.lang}</span>}
                </div>
              </button>
            </li>
          ))}
        </ul>
        {posts.data?.length === 0 && !adding && <p className="text-sm text-slate-500">No posts yet. Write your first one!</p>}
        <p className="mt-4 text-xs text-slate-400">
          Show your posts on a page by adding a “Blog posts” section there. Only published posts appear on the site.
        </p>
      </div>
    </aside>
  );
}
