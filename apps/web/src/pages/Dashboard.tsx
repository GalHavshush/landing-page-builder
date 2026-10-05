import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCreateProject, useDeleteProject, useLogout, useMe, useProjects, useTemplates } from "@/api/hooks";
import { Button, ErrorText, Field } from "@/components/ui";

export default function Dashboard() {
  const me = useMe();
  const projects = useProjects();
  const logout = useLogout();
  const del = useDeleteProject();

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Your sites</h1>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <span>{me.data?.email}</span>
          <Button variant="ghost" onClick={() => logout.mutate()}>Sign out</Button>
        </div>
      </header>
      <NewProject />
      <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.data?.map((p) => (
          <li key={p.id} className="group relative">
            <Link to={`/projects/${p.id}`} className="block rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:ring-indigo-400">
              <h2 className="font-medium">{p.name}</h2>
              <p className="mt-1 text-xs text-slate-500">
                {p.role === "owner" ? "Owner" : p.role === "editor" ? "Client access" : "Designer"} · {p.template_id}
              </p>
            </Link>
            {p.role === "owner" && (
              <button
                aria-label={`Delete ${p.name}`}
                title="Delete site"
                onClick={() => window.confirm(`Delete "${p.name}" and everything in it? This cannot be undone.`) && del.mutate(p.id)}
                className="absolute right-3 top-3 rounded px-1.5 text-slate-400 opacity-0 hover:text-red-600 focus:opacity-100 group-hover:opacity-100"
              >
                ✕
              </button>
            )}
          </li>
        ))}
      </ul>
      {projects.data?.length === 0 && <p className="mt-8 text-slate-500">No sites yet. Create your first one above.</p>}
    </div>
  );
}

function NewProject() {
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
    <form onSubmit={submit} className="space-y-4 rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <Field label="New site name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="Rosa's Bakery" />
      <fieldset>
        <legend className="mb-2 text-sm font-medium text-slate-700">Starting point</legend>
        <div className="grid gap-3 sm:grid-cols-3">
          {(templates.data ?? []).map((t) => (
            <label key={t.id} className={`cursor-pointer rounded-lg border p-3 text-sm transition ${template === t.id ? "border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500" : "border-slate-200 hover:border-slate-300"}`}>
              <input type="radio" name="template" value={t.id} checked={template === t.id} onChange={() => setTemplate(t.id)} className="sr-only" />
              <div className="font-medium">{t.label}</div>
              <div className="mt-0.5 text-xs text-slate-500">{t.description}</div>
            </label>
          ))}
        </div>
      </fieldset>
      <div className="flex items-center gap-3">
        <Button type="submit" disabled={create.isPending}>Create site</Button>
        <ErrorText>{create.error?.message}</ErrorText>
      </div>
    </form>
  );
}
