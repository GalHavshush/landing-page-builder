import { useEffect, useMemo, useRef, useState } from "react";
import { api, ApiError } from "@/api/client";
import { usePostMutations, usePosts } from "@/api/hooks";
import type { PostIn, PostOut } from "@/api/types";
import { Preview } from "../Preview";
import { useEditor } from "../store";
import { MarkdownEditor } from "./MarkdownEditor";
import { PostSettings } from "./PostSettings";

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;
type SaveState = "saved" | "dirty" | "saving" | "error";

export const toDraft = (p: PostOut): PostIn => ({
  lang: p.lang, title: p.title, slug: p.slug, excerpt: p.excerpt, body_md: p.body_md,
  cover_asset_id: p.cover_asset_id, status: p.status as PostIn["status"], published_at: p.published_at,
});

export function PostWorkspace() {
  const postId = useEditor((s) => s.postId);
  const projectId = useEditor((s) => s.projectId)!;
  const posts = usePosts(projectId);
  const post = posts.data?.find((p) => p.id === postId);

  if (!postId) return <Empty text="Pick a post on the left, or write a new one." />;
  if (posts.isPending) return <Empty text="Loading…" />;
  if (!post) return <Empty text="This post no longer exists." />;
  // key: a fresh editor (and fresh local state) for each post
  return <Editor key={post.id} post={post} />;
}

function Empty({ text }: { text: string }) {
  return <div className="col-span-2 grid place-items-center bg-ink-100 text-ink-500">{text}</div>;
}

function Editor({ post }: { post: PostOut }) {
  const projectId = useEditor((s) => s.projectId)!;
  const allPosts = usePosts(projectId).data ?? [];
  const { save } = usePostMutations(projectId);
  const [draft, setDraft] = useState<PostIn>(() => toDraft(post));
  const [state, setState] = useState<SaveState>("saved");
  const [error, setError] = useState<string | null>(null);
  const [html, setHtml] = useState<string>();
  const lastSaved = useRef(draft);

  const slugTaken = useMemo(
    () => allPosts.some((p) => p.id !== post.id && p.lang === draft.lang && p.slug === draft.slug),
    [allPosts, post.id, draft.lang, draft.slug],
  );
  const valid = draft.title.trim() !== "" && SLUG.test(draft.slug) && !slugTaken;
  const update = (patch: Partial<PostIn>) => {
    setDraft((d) => ({ ...d, ...patch }));
    setState("dirty");
  };

  // autosave a second after the last change (only when the post is valid)
  useEffect(() => {
    if (draft === lastSaved.current || !valid) return;
    const timer = setTimeout(() => {
      setState("saving");
      save.mutate(
        { id: post.id, body: draft },
        {
          onSuccess: (saved) => {
            lastSaved.current = draft;
            setError(null);
            setState((s) => (s === "saving" ? "saved" : s));
            // keep the shared list (status badge, titles) current without disturbing the editor
            allPostsCacheUpdate(projectId, saved);
          },
          onError: (e) => {
            setState("error");
            setError(e instanceof ApiError && e.status === 409 ? "Another post already uses this URL name." : e.message);
          },
        },
      );
    }, 1000);
    return () => clearTimeout(timer);
  }, [draft, valid]); // eslint-disable-line react-hooks/exhaustive-deps

  // live preview from the real renderer (debounced; latest wins)
  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await api<{ html: string }>(`/projects/${projectId}/posts/${post.id}/preview`, {
          method: "POST", body: draft, signal: controller.signal,
        });
        setHtml(res.html);
      } catch {
        /* keep the previous preview */
      }
    }, 400);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [draft, projectId, post.id]);

  const statusText = !valid ? "Fix the highlighted fields to save" : { saved: "All changes saved", dirty: "Unsaved changes…", saving: "Saving…", error: "Could not save" }[state];

  return (
    <div className="col-span-2 grid min-h-0 grid-cols-[1fr_320px]">
      <div className="grid min-h-0 grid-cols-2">
        <section className="flex min-h-0 flex-col border-r border-ink-200 bg-white">
          <div className="border-b border-ink-200 px-4 pt-3">
            <input aria-label="Post title" value={draft.title} onChange={(e) => update({ title: e.target.value })}
              placeholder="Post title" className="w-full text-xl font-semibold focus:outline-none" />
            <div role="status" className={`pb-2 text-xs ${valid && state !== "error" ? "text-ink-400" : "text-red-600"}`}>
              {statusText}{error ? `: ${error}` : ""}
            </div>
          </div>
          <MarkdownEditor value={draft.body_md ?? ""} onChange={(v) => update({ body_md: v })} />
        </section>
        <div className="min-h-0"><Preview html={html} /></div>
      </div>
      <PostSettings post={post} draft={draft} update={update} slugTaken={slugTaken} />
    </div>
  );
}

import { queryClient } from "@/api/queryClient";
function allPostsCacheUpdate(projectId: number, saved: PostOut) {
  queryClient.setQueryData<PostOut[]>(["posts", projectId], (old) =>
    old?.map((p) => (p.id === saved.id ? { ...saved, body_md: p.body_md === saved.body_md ? p.body_md : saved.body_md } : p)),
  );
}
