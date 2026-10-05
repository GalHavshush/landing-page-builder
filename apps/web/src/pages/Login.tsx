import { useState, type FormEvent } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useAuthMutation, useMe } from "@/api/hooks";
import { Button, ErrorText, Field } from "@/components/ui";

export default function Login() {
  const me = useMe();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  // only same-site paths: never redirect to a URL supplied by a link
  const rawNext = params.get("next") ?? "/";
  const next = rawNext.startsWith("/") && !rawNext.startsWith("//") ? rawNext : "/";
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const auth = useAuthMutation(mode);

  if (me.data) return <Navigate to={next} replace />;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    auth.mutate(form, { onSuccess: () => navigate(next) });
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-6 px-4">
      <div>
        <h1 className="text-2xl font-semibold">Site Builder</h1>
        <p className="text-sm text-slate-500">
          {mode === "login" ? "Sign in to your account" : "Create an account"}
        </p>
      </div>
      <form onSubmit={submit} className="flex flex-col gap-4 rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        {mode === "register" && (
          <Field label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        )}
        <Field label="Email" type="email" required autoComplete="email" value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <Field label="Password" type="password" required minLength={8}
          autoComplete={mode === "login" ? "current-password" : "new-password"} value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <ErrorText>{auth.error?.message}</ErrorText>
        <Button type="submit" disabled={auth.isPending}>
          {mode === "login" ? "Sign in" : "Create account"}
        </Button>
      </form>
      <button className="text-sm text-indigo-600 hover:underline" onClick={() => { auth.reset(); setMode(mode === "login" ? "register" : "login"); }}>
        {mode === "login" ? "New here? Create an account" : "Have an account? Sign in"}
      </button>
    </main>
  );
}
