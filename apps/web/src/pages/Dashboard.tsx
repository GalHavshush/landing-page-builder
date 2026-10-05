import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCreateProject, useDeleteProject, useLogout, useMe, useProjects, useTemplates } from "@/api/hooks";
import { IconClose, IconPlus } from "@/components/icons";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button, ErrorText, Field } from "@/components/ui";

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

export default function Dashboard() {
  const me = useMe();
  const projects = useProjects();
  const allTemplates = useTemplates();
  const logout = useLogout();
  const del = useDeleteProject();
  const [creating, setCreating] = useState(false);

  return (
    <div className="min-h-screen">
      <header className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex h-12 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2 text-[13px] font-semibold tracking-tight">
            <span className="grid h-5 w-5 place-items-center rounded-[4px] bg-ink-900 font-mono text-[10px] text-white">S</span>
            Sitebook
          </div>
          <div className="flex items-center gap-3 text-[13px] text-ink-600">
            <ThemeToggle />
            <span>{me.data?.email}</span>
            <Button variant="quiet" onClick={() => logout.mutate()}>Sign out</Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h1 className="text-[26px] font-semibold tracking-[-0.025em]">Your sites</h1>
            <p className="mt-1 text-[13px] text-ink-500">{projects.data ? `${projects.data.length} ${projects.data.length === 1 ? "site" : "sites"}` : " "}</p>
          </div>
          {!creating && <Button onClick={() => setCreating(true)}><IconPlus size={14} />New site</Button>}
        </div>

        {creating && <NewProject onDone={() => setCreating(false)} />}

        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.data?.map((p) => (
            <li key={p.id} className="group relative">
              <Link to={`/projects/${p.id}`}
                className="block rounded-xl border border-ink-200 bg-white p-4 transition duration-200 hover:-translate-y-0.5 hover:border-ink-300 hover:shadow-[0_8px_24px_-12px_rgb(27_26_23/0.25)]">
                <Swatches palette={allTemplates.data?.find((t) => t.id === p.template_id)?.theme.palette ?? { background: "#fff", text: "#111", primary: "#2563EB", accent: "#F59E0B" }} />
                <h2 className="mt-4 truncate text-[15px] font-semibold tracking-tight">{p.name}</h2>
                <p className="mt-0.5 flex items-center gap-1.5 text-[12px] text-ink-500">
                  {ROLE_LABEL[p.role] ?? p.role}<span className="text-ink-300">/</span><span className="font-mono">{p.slug}</span>
                </p>
              </Link>
              {p.role === "owner" && (
                <button aria-label={`Delete ${p.name}`} title="Delete site"
                  onClick={() => window.confirm(`Delete "${p.name}" and everything in it? This cannot be undone.`) && del.mutate(p.id)}
                  className="absolute right-3 top-3 grid h-6 w-6 place-items-center rounded-md bg-white/90 text-ink-500 opacity-0 shadow-sm ring-1 ring-ink-200 transition hover:bg-red-600 hover:text-white hover:ring-red-600 focus:opacity-100 group-hover:opacity-100">
                  <IconClose size={13} />
                </button>
              )}
            </li>
          ))}
        </ul>
        {projects.data?.length === 0 && !creating && (
          <div className="rounded-xl border border-dashed border-ink-300 p-12 text-center">
            <p className="text-[15px] font-medium">No sites yet</p>
            <p className="mt-1 text-[13px] text-ink-500">Pick a starting point and you'll be editing in seconds.</p>
            <Button className="mt-4" onClick={() => setCreating(true)}><IconPlus size={14} />New site</Button>
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

  const submit = (e: FormEvent) => {
    e.preventDefault();
    create.mutate({ name, template }, { onSuccess: (p) => navigate(`/projects/${p.id}`) });
  };

  return (
    <form onSubmit={submit} className="mb-8 rounded-xl border border-ink-200 bg-white p-5">
      <div className="max-w-sm">
        <Field label="Site name" required autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Rosa's Bakery" />
      </div>
      <fieldset className="mt-5">
        <legend className="field-label mb-2">Starting point</legend>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {(templates.data ?? []).map((t) => (
            <label key={t.id} className={`cursor-pointer rounded-lg border p-3 transition ${template === t.id ? "border-ink-900 shadow-[0_0_0_1px_var(--color-ink-900)]" : "border-ink-200 hover:border-ink-400"}`}>
              <input type="radio" name="template" value={t.id} checked={template === t.id} onChange={() => setTemplate(t.id)} className="sr-only" />
              <Swatches palette={t.theme.palette} />
              <div className="mt-3 text-[13px] font-medium">{t.label}</div>
              <div className="mt-0.5 text-[12px] leading-snug text-ink-500">{t.description}</div>
            </label>
          ))}
        </div>
      </fieldset>
      {(templates.data?.find((t) => t.id === template)?.photo_hints ?? []).length > 0 && (
        <p className="mt-3 text-[12px] text-ink-500">
          Add photos for the best result: {templates.data!.find((t) => t.id === template)!.photo_hints.join(" · ")}.
        </p>
      )}
      <div className="mt-5 flex items-center gap-2">
        <Button type="submit" disabled={create.isPending}>Create site</Button>
        <Button type="button" variant="quiet" onClick={onDone}>Cancel</Button>
        <ErrorText>{create.error?.message}</ErrorText>
      </div>
    </form>
  );
}
