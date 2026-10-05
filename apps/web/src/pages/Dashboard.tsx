import { useState, type FormEvent } from "react";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/api/client";
import { useCreateProject, useDeleteProject, useEditorMeta, useLogout, useMe, useProjects, useTemplates } from "@/api/hooks";
import { IconClose, IconEye, IconPlus, IconSettings } from "@/components/icons";
import { LivePreview } from "@/components/LivePreview";
import { Button, ErrorText, Field } from "@/components/ui";
import { getUiLang, t } from "@/i18n";

const ROLE_LABEL: Record<string, string> = { owner: "Owner", designer: "Designer", editor: "Client access" };

// A tiny stand-in for each starter's look, drawn from its palette (no screenshots needed).
function Swatches({ palette }: { palette: Record<string, string> }) {
  return (
    <div className="flex h-9 overflow-hidden rounded-md ring-1 ring-inset ring-black/10" aria-hidden>
      <div className="flex-[3]" style={{ background: palette.background }}><div className="m-2 h-1.5 w-8 rounded-full" style={{ background: palette.text }} /><div className="mx-2 h-1 w-12 rounded-full opacity-40" style={{ background: palette.text }} /></div>
      <div className="flex-1" style={{ background: palette.primary }} />
      <div className="flex-1" style={{ background: palette.accent }} />
    </div>
  );
}

const THUMB_W = 1280; // the page is laid out as on a laptop, then scaled down to the card

/** A small, live picture of the site's first page (falls back to the colour swatches). */
function SiteThumb({ projectId, palette }: { projectId: number; palette: Record<string, string> }) {
  const html = useQuery({ queryKey: ["live", projectId], queryFn: () => api<{ html: string }>(`/projects/${projectId}/live`), retry: false });
  const box = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(0.25);
  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setScale(el.clientWidth / THUMB_W));
    ro.observe(el);
    return () => ro.disconnect();
  }, [html.data]);
  if (!html.data) return <Swatches palette={palette} />;
  return (
    <div ref={box} aria-hidden className="relative aspect-[16/10] overflow-hidden rounded-md bg-white ring-1 ring-inset ring-black/10">
      <iframe title="" tabIndex={-1} srcDoc={html.data.html} sandbox="allow-scripts"
        className="pointer-events-none absolute left-0 top-0 origin-top-left border-0"
        style={{ width: THUMB_W, height: THUMB_W * 0.625, transform: `scale(${scale})` }} />
    </div>
  );
}

export default function Dashboard() {
  const me = useMe();
  const projects = useProjects();
  const allTemplates = useTemplates();
  const logout = useLogout();
  const del = useDeleteProject();
  const [creating, setCreating] = useState(false);
  const [previewing, setPreviewing] = useState<{ id: number; name: string } | null>(null);

  return (
    <div className="min-h-screen">
      <header className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex h-12 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2 text-[13px] font-semibold tracking-tight">
            <span className="grid h-5 w-5 place-items-center rounded-[4px] bg-ink-900 font-mono text-[10px] text-white">S</span>
            Sitebook
          </div>
          <div className="flex items-center gap-3 text-[13px] text-ink-600">
            <Link to="/settings" aria-label={t("Settings")} title={t("Settings")} className="grid h-7 w-7 place-items-center rounded-md text-ink-600 transition hover:bg-ink-100 hover:text-ink-900"><IconSettings size={15} /></Link>
            <span>{me.data?.email}</span>
            <Button variant="quiet" onClick={() => logout.mutate()}>{t("Sign out")}</Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h1 className="text-[26px] font-semibold tracking-[-0.025em]">{t("Your sites")}</h1>
            <p className="mt-1 text-[13px] text-ink-500">{projects.data ? (projects.data.length === 1 ? t("1 site") : t("{n} sites", { n: projects.data.length })) : " "}</p>
          </div>
          {!creating && <Button onClick={() => setCreating(true)}><IconPlus size={14} />{t("New site")}</Button>}
        </div>

        {creating && <NewProject onDone={() => setCreating(false)} />}
        {previewing && (
          <LivePreview title={previewing.name} onClose={() => setPreviewing(null)}
            load={async (to, signal) => {
              const q = new URLSearchParams();
              if (to.page) q.set("page_id", to.page);
              if (to.lang) q.set("lang", to.lang);
              return (await api<{ html: string }>(`/projects/${previewing.id}/live?${q}`, { signal })).html;
            }}
          />
        )}

        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.data?.map((p) => (
            <li key={p.id} className="group relative">
              <Link to={`/projects/${p.id}`}
                className="block rounded-xl border border-ink-200 bg-white p-4 transition duration-200 hover:-translate-y-0.5 hover:border-ink-300 hover:shadow-[0_8px_24px_-12px_rgb(27_26_23/0.25)]">
                <SiteThumb projectId={p.id} palette={allTemplates.data?.find((x) => x.id === p.template_id)?.theme.palette ?? { background: "#fff", text: "#111", primary: "#2563EB", accent: "#F59E0B" }} />
                <h2 className="mt-4 truncate text-[15px] font-semibold tracking-tight">{p.name}</h2>
                <p className="mt-0.5 flex items-center gap-1.5 text-[12px] text-ink-500">
                  {t(ROLE_LABEL[p.role] ?? p.role)}<span className="text-ink-300">/</span><span className="font-mono">{p.slug}</span>
                </p>
              </Link>
              <button aria-label={t("Preview {name}", { name: p.name })} title={t("Preview")} onClick={() => setPreviewing(p)}
                className="absolute start-3 top-3 grid h-6 w-6 place-items-center rounded-md bg-white/90 text-ink-500 opacity-0 shadow-sm ring-1 ring-ink-200 transition hover:bg-ink-900 hover:text-white hover:ring-ink-900 focus:opacity-100 group-hover:opacity-100">
                <IconEye size={13} />
              </button>
              {p.role === "owner" && (
                <button aria-label={t("Delete {name}", { name: p.name })} title={t("Delete site")}
                  onClick={() => window.confirm(t("Delete \"{name}\" and everything in it? This cannot be undone.", { name: p.name })) && del.mutate(p.id)}
                  className="absolute end-3 top-3 grid h-6 w-6 place-items-center rounded-md bg-white/90 text-ink-500 opacity-0 shadow-sm ring-1 ring-ink-200 transition hover:bg-red-600 hover:text-white hover:ring-red-600 focus:opacity-100 group-hover:opacity-100">
                  <IconClose size={13} />
                </button>
              )}
            </li>
          ))}
        </ul>
        {projects.data?.length === 0 && !creating && (
          <div className="rounded-xl border border-dashed border-ink-300 p-12 text-center">
            <p className="text-[15px] font-medium">{t("No sites yet")}</p>
            <p className="mt-1 text-[13px] text-ink-500">{t("Pick a starting point and you'll be editing in seconds.")}</p>
            <Button className="mt-4" onClick={() => setCreating(true)}><IconPlus size={14} />{t("New site")}</Button>
          </div>
        )}
      </main>
    </div>
  );
}

function NewProject({ onDone }: { onDone: () => void }) {
  const templates = useTemplates();
  const create = useCreateProject();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [template, setTemplate] = useState("clean");
  const meta = useEditorMeta();
  const [language, setLanguage] = useState<string>(getUiLang()); // the editor language, to start with
  const [extra, setExtra] = useState<string[]>([]);
  const names = meta.data?.languages ?? { en: "English" };
  const others = Object.keys(names).filter((c) => c !== language);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    create.mutate({ name, template, language, extra_languages: extra.filter((c) => c !== language) }, { onSuccess: (p) => navigate(`/projects/${p.id}`) });
  };

  return (
    <form onSubmit={submit} className="mb-8 rounded-xl border border-ink-200 bg-white p-5">
      <div className="max-w-sm">
        <Field label={t("Site name")} required autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder={t("Rosa's Bakery")} />
      </div>
      <fieldset className="mt-5 max-w-lg">
        <legend className="field-label mb-2">{t("Languages")}</legend>
        <label className="block text-[12px] text-ink-500" htmlFor="main-language">{t("Main language")}</label>
        <select id="main-language" value={language} onChange={(e) => setLanguage(e.target.value)} className="field-input mt-1 max-w-xs">
          {Object.entries(names).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
        </select>
        <p className="mt-3 text-[12px] text-ink-500">{t("Also offer the site in (optional)")}</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {others.map((c) => (
            <label key={c} className={`cursor-pointer rounded-full border px-2.5 py-1 text-[12px] transition ${extra.includes(c) ? "border-ink-900 bg-ink-100" : "border-ink-200 hover:border-ink-400"}`}>
              <input type="checkbox" className="sr-only" checked={extra.includes(c)}
                onChange={() => setExtra(extra.includes(c) ? extra.filter((x) => x !== c) : [...extra, c])} />
              {names[c]}
            </label>
          ))}
        </div>
      </fieldset>
      <fieldset className="mt-5">
        <legend className="field-label mb-2">{t("Starting point")}</legend>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {(templates.data ?? []).map((tpl) => (
            <label key={tpl.id} className={`cursor-pointer rounded-lg border p-3 transition ${template === tpl.id ? "border-ink-900 shadow-[0_0_0_1px_var(--color-ink-900)]" : "border-ink-200 hover:border-ink-400"}`}>
              <input type="radio" name="template" value={tpl.id} checked={template === tpl.id} onChange={() => setTemplate(tpl.id)} className="sr-only" />
              <Swatches palette={tpl.theme.palette} />
              <div className="mt-3 text-[13px] font-medium">{t(tpl.label)}</div>
              <div className="mt-0.5 text-[12px] leading-snug text-ink-500">{t(tpl.description)}</div>
            </label>
          ))}
        </div>
      </fieldset>
      {(templates.data?.find((x) => x.id === template)?.photo_hints ?? []).length > 0 && (
        <p className="mt-3 text-[12px] text-ink-500">
          {t("Add photos for the best result:")} {templates.data!.find((x) => x.id === template)!.photo_hints.map((h) => t(h)).join(" · ")}.
        </p>
      )}
      <div className="mt-5 flex items-center gap-2">
        <Button type="submit" disabled={create.isPending}>{t("Create site")}</Button>
        <Button type="button" variant="quiet" onClick={onDone}>{t("Cancel")}</Button>
        <ErrorText>{create.error?.message}</ErrorText>
      </div>
    </form>
  );
}
