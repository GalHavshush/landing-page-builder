import { useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCreateFromBrief } from "@/api/hooks";
import { IconBack, IconChevronRight } from "@/components/icons";
import { Button } from "@/components/ui";
import { getUiLang, tIn, type UiLang } from "@/i18n";
import { initialDraft, previewPage, stepError, stepsFor, toBrief, type Draft, type Group } from "@/newsite/model";
import { SitePreview } from "@/newsite/SitePreview";
import { STEP_VIEW } from "@/newsite/steps";

const GROUPS: Group[] = ["basics", "pages", "content", "look"];
const GROUP_LABEL: Record<Group, string> = { basics: "Basics", pages: "Pages", content: "Content", look: "Look" };

/** The form is written in the site's language (Hebrew or English; anything else reads English). */
const formLang = (language: string): UiLang => (language === "he" ? "he" : "en");

/**
 * Guided way to start a site: a step-by-step form that ends in the (unchanged) editor, already
 * filled with the answers. A live preview shows the site taking shape next to the questions.
 */
export default function NewSite() {
  const navigate = useNavigate();
  const create = useCreateFromBrief();
  const [d, setD] = useState<Draft>(() => initialDraft(getUiLang()));
  const [index, setIndex] = useState(0);
  const [shown, setShown] = useState(false); // show the step's problem only after a failed Next

  const lang = formLang(d.language);
  const T = useMemo(() => (text: string, vars?: Record<string, string | number>) => tIn(lang, text, vars), [lang]);
  const steps = stepsFor(d.pages);
  const at = Math.min(index, steps.length - 1);
  const step = steps[at];
  const view = STEP_VIEW[step.id];
  const error = stepError(step.id, d);
  const last = at === steps.length - 1;
  const brief = useMemo(() => toBrief(d), [d]);

  const set = (patch: Partial<Draft>) => { setD((prev) => ({ ...prev, ...patch })); setShown(false); };
  const go = (to: number) => { setIndex(to); setShown(false); window.scrollTo({ top: 0 }); };

  const next = (e?: FormEvent) => {
    e?.preventDefault();
    if (error) return setShown(true);
    if (!last) return go(at + 1);
    create.mutate({ ...brief, name: d.name.trim() }, { onSuccess: (p) => navigate(`/projects/${p.id}`) });
  };

  return (
    <div dir={lang === "he" ? "rtl" : "ltr"} lang={lang} className="min-h-screen">
      <header className="border-b border-ink-200 bg-white">
        <div className="mx-auto flex h-12 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2 text-[13px] font-semibold tracking-tight">
            <span className="grid h-5 w-5 place-items-center rounded-[4px] bg-ink-900 font-mono text-[10px] text-white">S</span>
            {T("New site")}
          </div>
          <Link to="/" className="text-[13px] text-ink-600 hover:text-ink-900">{T("Cancel")}</Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <nav aria-label={T("Progress")} className="mb-8">
          <ol className="flex gap-1">
            {steps.map((s, i) => (
              <li key={s.id} className="flex-1">
                <button type="button" disabled={i > at} onClick={() => go(i)} aria-label={T(STEP_VIEW[s.id].title)} aria-current={i === at ? "step" : undefined}
                  className={`block h-1 w-full rounded-full transition ${i < at ? "bg-ink-900" : i === at ? "bg-accent-500" : "bg-ink-200"}`} />
              </li>
            ))}
          </ol>
          <div className="mt-1.5 flex text-[11px] text-ink-400">
            {GROUPS.map((g) => {
              const n = steps.filter((s) => s.group === g).length;
              return <span key={g} style={{ flex: n }} className={step.group === g ? "font-medium text-accent-600" : ""}>{T(GROUP_LABEL[g])}</span>;
            })}
          </div>
        </nav>

        <div className="grid gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
          <form onSubmit={next} noValidate>
            <p className="text-[12px] text-ink-500">{T("Step {n} of {total}", { n: at + 1, total: steps.length })}</p>
            <h1 className="mt-1 text-[24px] font-semibold tracking-[-0.025em]">{T(view.title)}</h1>
            <p className="mb-6 mt-1 text-[13px] text-ink-500">{T(view.help)}</p>

            <view.View d={d} set={set} T={T} />

            {shown && error && <p role="alert" className="mt-4 text-[13px] text-red-600">{T(error)}</p>}
            {create.error && <p role="alert" className="mt-4 text-[13px] text-red-600">{T("Couldn't create the site. Try again.")}</p>}

            <div className="mt-8 flex items-center justify-between border-t border-ink-200 pt-4">
              <Button type="button" variant="ghost" disabled={at === 0} onClick={() => go(at - 1)}><IconBack size={14} />{T("Back")}</Button>
              <div className="flex items-center gap-3">
                {view.optional && !last && (
                  <button type="button" onClick={() => next()} className="text-[13px] text-ink-500 hover:text-ink-900">{T("Skip this step")}</button>
                )}
                <Button type="submit" disabled={create.isPending}>
                  {last ? (create.isPending ? T("Creating…") : T("Create site")) : <>{T("Next")}<IconChevronRight size={14} /></>}
                </Button>
              </div>
            </div>
          </form>

          <aside className="lg:sticky lg:top-6 lg:self-start">
            <SitePreview brief={{ ...brief, name: d.name.trim() || T("Your business") }} pageId={previewPage(step.id)} T={T} />
          </aside>
        </div>
      </main>
    </div>
  );
}
