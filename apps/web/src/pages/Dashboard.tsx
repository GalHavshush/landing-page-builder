import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCreateProject, useLogout, useMe, useProjects, useTemplates } from "@/api/hooks";
import { Button, ErrorText, Field } from "@/components/ui";

export default function Dashboard() {
  const me = useMe();
  const projects = useProjects();
  const logout = useLogout();

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
          <li key={p.id}>
            <Link to={`/projects/${p.id}`} className="block rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200 transition hover:ring-indigo-400">
              <h2 className="font-medium">{p.name}</h2>
              <p className="mt-1 text-xs text-slate-500">
                {p.role} · template: {p.template_id}
              </p>
            </Link>
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
    <form onSubmit={submit} className="flex flex-wrap items-end gap-3 rounded-xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="min-w-60 flex-1">
        <Field label="New site name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="Rosa Bakery" />
      </div>
      <label className="text-sm font-medium text-slate-700">
        Template
        <select className="mt-1 block rounded-md border border-slate-300 bg-white px-3 py-2 text-sm" value={template} onChange={(e) => setTemplate(e.target.value)}>
          {(templates.data ?? ["clean"]).map((t) => <option key={t}>{t}</option>)}
        </select>
      </label>
      <Button type="submit" disabled={create.isPending}>Create site</Button>
      <ErrorText>{create.error?.message}</ErrorText>
    </form>
  );
}
