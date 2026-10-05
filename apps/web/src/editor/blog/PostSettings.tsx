import { useEffect, useState } from "react";
import { usePostMutations, usePosts } from "@/api/hooks";
import type { PostIn, PostOut } from "@/api/types";
import { Button } from "@/components/ui";
import { SegmentedControl, TextAreaControl } from "../controls/basic";
import { ImageControl } from "../controls/ImageControl";
import { useEditor } from "../store";
import { t } from "@/i18n";

const SLUG = /^[a-z0-9]+(-[a-z0-9]+)*$/;

export function PostSettings({
  post, draft, update, slugTaken,
}: {
  post: PostOut;
  draft: PostIn;
  update: (patch: Partial<PostIn>) => void;
  slugTaken: boolean;
}) {
  const projectId = useEditor((s) => s.projectId)!;
  const doc = useEditor((s) => s.doc)!;
  const openPost = useEditor((s) => s.openPost);
  const all = usePosts(projectId).data ?? [];
  const { remove, translate } = usePostMutations(projectId);
  const [slug, setSlug] = useState(draft.slug);
  useEffect(() => setSlug(draft.slug), [draft.slug]);
  const slugProblem = !SLUG.test(slug) ? t("Lowercase letters, numbers and single hyphens only") : slugTaken ? t("Another post in this language uses this") : null;
  const siblings = all.filter((p) => p.translation_group === post.translation_group && p.id !== post.id);
  const missing = doc.site.languages.filter((l) => l !== draft.lang && !siblings.some((s) => s.lang === l));
  const date = (draft.published_at ?? "").slice(0, 10);

  return (
    <aside className="min-h-0 space-y-5 overflow-y-auto border-s border-ink-200 bg-white p-4">
      <h2 className="text-sm font-semibold">{t("Post settings")}</h2>
      <SegmentedControl label="Status" value={draft.status} options={[{ value: "draft", label: "Draft" }, { value: "published", label: "Published" }]}
        onChange={(v) => update({ status: v as PostIn["status"] })} />
      {draft.status === "draft" && <p className="-mt-3 text-xs text-ink-400">{t("Drafts are never part of the site or its export.")}</p>}
      <div>
        <label htmlFor="post-date" className="block text-xs font-medium text-ink-600">{t("Publish date")}</label>
        <input id="post-date" type="date" value={date} onChange={(e) => update({ published_at: e.target.value ? `${e.target.value}T12:00:00Z` : null })}
          className="mt-1 block w-full rounded-md border border-ink-300 px-2.5 py-1.5 text-sm" />
        <p className="mt-1 text-xs text-ink-400">{t("Empty: set automatically when you publish.")}</p>
      </div>
      <div>
        <label htmlFor="post-slug" className="block text-xs font-medium text-ink-600">{t("URL name")}</label>
        <div className="mt-1 flex items-center rounded-md border border-ink-300 text-sm">
          <span className="ps-2.5 text-ink-400" dir="ltr">/blog/</span>
          <input id="post-slug" dir="ltr" value={slug} aria-invalid={Boolean(slugProblem)} spellCheck={false}
            onChange={(e) => { const v = e.target.value.toLowerCase(); setSlug(v); if (v) update({ slug: v }); }}
            className="w-full rounded-md bg-transparent px-1 py-1.5 focus:outline-none" />
        </div>
        {slugProblem && <p className="mt-1 text-xs text-red-600">{slugProblem}</p>}
      </div>
      <TextAreaControl label="Summary" value={draft.excerpt ?? ""} onChange={(v) => update({ excerpt: v })}
        hint="Shown in lists and in search/social previews." />
      <ImageControl label="Cover image" hideAlt value={draft.cover_asset_id ? { asset: draft.cover_asset_id, alt: "", focus: { x: 50, y: 50 } } : null}
        onChange={(v) => update({ cover_asset_id: v?.asset ?? null })} />
      {doc.site.languages.length > 1 && (
        <div>
          <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-500">{t("Translations")}</h3>
          <ul className="space-y-1 text-sm">
            <li className="text-ink-500">{t("This post:")} <strong>{draft.lang}</strong></li>
            {siblings.map((s) => (
              <li key={s.id}><button className="text-ink-700 underline decoration-ink-300 underline-offset-2 hover:decoration-ink-900" onClick={() => openPost(s.id)}>{t("Edit {lang} version", { lang: s.lang })}</button></li>
            ))}
            {missing.map((l) => (
              <li key={l}>
                <button className="text-ink-700 underline decoration-ink-300 underline-offset-2 hover:decoration-ink-900" disabled={translate.isPending}
                  onClick={() => translate.mutate({ id: post.id, lang: l }, { onSuccess: (p) => openPost(p.id) })}>
                  {t("Translate to {lang}", { lang: l })}
                </button>
              </li>
            ))}
          </ul>
          <p className="mt-1 text-xs text-ink-400">{t("Translating copies the text as a new draft to start from.")}</p>
        </div>
      )}
      <div className="border-t border-ink-200 pt-4">
        <Button variant="danger" className="w-full"
          onClick={() => window.confirm(t("Delete this post permanently?")) && remove.mutate(post.id, { onSuccess: () => openPost(null) })}>
          {t("Delete post")}
        </Button>
      </div>
    </aside>
  );
}
