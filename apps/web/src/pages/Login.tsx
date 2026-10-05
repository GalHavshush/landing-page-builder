import { useState, type FormEvent } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { useAuthMutation, useMe } from "@/api/hooks";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button, ErrorText, Field } from "@/components/ui";

/** A calm two-column sign-in: a typographic statement on the left, the form on the right. */
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
    <main className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <section className="fixed-dark-panel relative hidden flex-col justify-between overflow-hidden bg-ink-900 p-12 text-ink-50 lg:flex">
        <div className="flex items-center gap-2 text-[13px] font-medium tracking-tight">
          <span className="grid h-6 w-6 place-items-center rounded-[5px] bg-ink-50 font-mono text-[11px] font-semibold text-ink-900">S</span>
          Sitebook
        </div>
        <div>
          <p className="max-w-[16ch] text-[56px] font-semibold leading-[1.02] tracking-[-0.035em]">
            Small sites, <span className="text-accent-400">made well.</span>
          </p>
          <p className="mt-6 max-w-[40ch] text-[15px] leading-relaxed text-ink-300">
            Build fast, static websites from ready-made sections. Hand them to a client with a simple editor. Export and host anywhere, no lock-in.
          </p>
        </div>
        <dl className="grid max-w-md grid-cols-3 gap-6 border-t border-ink-700 pt-6 text-[12px]">
          {[["Static", "plain HTML, CSS"], ["Exportable", "one ZIP, any host"], ["Bilingual", "RTL ready"]].map(([k, v]) => (
            <div key={k}>
              <dt className="font-medium text-ink-50">{k}</dt>
              <dd className="mt-0.5 text-ink-400">{v}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="relative flex items-center justify-center px-6 py-12">
        <div className="absolute right-5 top-5"><ThemeToggle /></div>
        <div className="w-full max-w-[340px]">
          <h1 className="text-[22px] font-semibold tracking-[-0.02em]">{mode === "login" ? "Welcome back" : "Create your account"}</h1>
          <p className="mt-1 text-[13px] text-ink-500">{mode === "login" ? "Sign in to continue to your sites." : "Start with a template, finish in minutes."}</p>
          <form onSubmit={submit} className="mt-7 space-y-4">
            {mode === "register" && <Field label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />}
            <Field label="Email" type="email" required autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <Field label="Password" type="password" required minLength={8} autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <ErrorText>{auth.error?.message}</ErrorText>
            <Button type="submit" disabled={auth.isPending} className="h-9 w-full">
              {mode === "login" ? "Sign in" : "Create account"}
            </Button>
          </form>
          <button className="mt-5 text-[13px] text-ink-600 underline decoration-ink-300 underline-offset-4 transition hover:text-ink-900 hover:decoration-ink-900"
            onClick={() => { auth.reset(); setMode(mode === "login" ? "register" : "login"); }}>
            {mode === "login" ? "New here? Create an account" : "Have an account? Sign in"}
          </button>
        </div>
      </section>
    </main>
  );
}
