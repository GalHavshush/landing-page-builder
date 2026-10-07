import type { ReactNode } from "react";
import { useEditorMeta, useTemplates } from "@/api/hooks";
import { IconClose, IconPlus } from "@/components/icons";
import { Swatches } from "@/components/Swatches";
import { Button } from "@/components/ui";
import {
  blank, PAGE_ORDER, SOCIALS, STARTER_FOR_TYPE,
  type BusinessType, type Draft, type GoalKind, type PageKind, type StepId, type Tf,
} from "./model";

export interface StepProps { d: Draft; set: (patch: Partial<Draft>) => void; T: Tf }

/* ---------- small building blocks ---------- */

function Input({ label, value, onChange, placeholder, type = "text", ltr, autoFocus }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string; ltr?: boolean; autoFocus?: boolean;
}) {
  return (
    <label className="block">
      <span className="field-label">{label}</span>
      <input type={type} value={value} placeholder={placeholder} autoFocus={autoFocus} dir={ltr ? "ltr" : undefined}
        onChange={(e) => onChange(e.target.value)} className={`field-input mt-1 ${ltr ? "text-start" : ""}`} />
    </label>
  );
}

function Area({ label, value, onChange, placeholder, rows = 4 }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; rows?: number;
}) {
  return (
    <label className="block">
      <span className="field-label">{label}</span>
      <textarea rows={rows} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} className="field-input mt-1 h-auto py-2 leading-relaxed" />
    </label>
  );
}

function Choice({ checked, onChange, type, name, title, hint, children }: {
  checked: boolean; onChange: () => void; type: "radio" | "checkbox"; name?: string; title: string; hint?: string; children?: ReactNode;
}) {
  return (
    <label className={`block cursor-pointer rounded-lg border p-3 transition ${checked ? "border-ink-900 shadow-[0_0_0_1px_var(--color-ink-900)]" : "border-ink-200 hover:border-ink-400"}`}>
      <input type={type} name={name} checked={checked} onChange={onChange} className="sr-only" />
      {children}
      <div className="text-[13px] font-medium">{title}</div>
      {hint && <div className="mt-0.5 text-[12px] leading-snug text-ink-500">{hint}</div>}
    </label>
  );
}

/** Repeatable cards: the form starts with a few empty ones so typing can begin at once. */
function ItemList<I>({ T, items, onChange, make, addLabel, render }: {
  T: Tf; items: I[]; onChange: (items: I[]) => void; make: () => I; addLabel: string;
  render: (item: I, update: (patch: Partial<I>) => void) => ReactNode;
}) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="rounded-lg border border-ink-200 bg-white p-3">
          <div className="mb-2 flex items-center justify-between text-[12px] text-ink-500">
            <span>{i + 1}</span>
            <button type="button" aria-label={T("Remove")} title={T("Remove")} onClick={() => onChange(items.filter((_, j) => j !== i))}
              className="grid h-6 w-6 place-items-center rounded hover:bg-ink-100 hover:text-ink-900"><IconClose size={13} /></button>
          </div>
          <div className="space-y-2">{render(item, (patch) => onChange(items.map((x, j) => (j === i ? { ...x, ...patch } : x))))}</div>
        </div>
      ))}
      <Button type="button" variant="ghost" className="w-full border-dashed" onClick={() => onChange([...items, make()])}>
        <IconPlus size={13} />{addLabel}
      </Button>
    </div>
  );
}

const grid2 = "grid gap-2 sm:grid-cols-2";

/* ---------- steps ---------- */

function LanguageStep({ d, set, T }: StepProps) {
  const names = useEditorMeta().data?.languages ?? { en: "English", he: "עברית" };
  const others = Object.keys(names).filter((c) => c !== d.language);
  return (
    <div className="space-y-5">
      <label className="block">
        <span className="field-label">{T("Main language")}</span>
        <select value={d.language} onChange={(e) => set({ language: e.target.value, extra_languages: d.extra_languages.filter((c) => c !== e.target.value) })}
          className="field-input mt-1 max-w-xs">
          {Object.entries(names).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
        </select>
      </label>
      <fieldset>
        <legend className="field-label">{T("Also offer the site in (optional)")}</legend>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {others.map((c) => (
            <label key={c} className={`cursor-pointer rounded-full border px-2.5 py-1 text-[12px] transition ${d.extra_languages.includes(c) ? "border-ink-900 bg-ink-100" : "border-ink-200 hover:border-ink-400"}`}>
              <input type="checkbox" className="sr-only" checked={d.extra_languages.includes(c)}
                onChange={() => set({ extra_languages: d.extra_languages.includes(c) ? d.extra_languages.filter((x) => x !== c) : [...d.extra_languages, c] })} />
              {names[c]}
            </label>
          ))}
        </div>
      </fieldset>
    </div>
  );
}

export const TYPE_LABELS: [BusinessType, string][] = [
  ["general", "Business or company"], ["local_shop", "Local shop or bakery"], ["restaurant", "Restaurant or café"],
  ["salon", "Salon or beauty"], ["trades", "Trades and repairs"], ["clinic", "Clinic or wellbeing"],
  ["photographer", "Photographer"], ["consultant", "Consultant or agency"], ["fitness", "Gym or fitness"],
  ["garden", "Garden and landscaping"], ["portfolio", "Portfolio or freelancer"],
];

function BusinessStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-5">
      <Input autoFocus label={T("Business name")} value={d.name} onChange={(name) => set({ name })} placeholder={T("Rosa's Bakery")} />
      <fieldset>
        <legend className="field-label mb-1.5">{T("What kind of business is it?")}</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {TYPE_LABELS.map(([id, label]) => (
            <Choice key={id} type="radio" name="type" checked={d.business_type === id} onChange={() => set({ business_type: id, template: null })} title={T(label)} />
          ))}
        </div>
      </fieldset>
      <Input label={T("Tagline")} value={d.tagline} onChange={(tagline) => set({ tagline })} placeholder={T("Bread worth waking up for")} />
      <Area rows={3} label={T("A short description")} value={d.description} onChange={(description) => set({ description })}
        placeholder={T("Two sentences about what you do and who it's for.")} />
    </div>
  );
}

export const GOALS: [GoalKind, string, string][] = [
  ["call", "Call us", "Visitors tap to phone you."],
  ["book", "Book online", "Visitors go to your booking page."],
  ["message", "Send a message", "Visitors use your contact page."],
  ["visit", "Visit us", "Visitors find your address and opening hours."],
];

function GoalStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-2 sm:grid-cols-2">
        {GOALS.map(([id, label, hint]) => (
          <Choice key={id} type="radio" name="goal" checked={d.goal.kind === id} onChange={() => set({ goal: { ...d.goal, kind: id } })} title={T(label)} hint={T(hint)} />
        ))}
      </div>
      {d.goal.kind === "book" && (
        <Input ltr label={T("Booking link")} value={d.goal.url} onChange={(url) => set({ goal: { ...d.goal, url } })} placeholder="https://" />
      )}
      {d.goal.kind === "call" && !d.phone.trim() && <p className="text-[12px] text-ink-500">{T("Add your phone number on the next step.")}</p>}
    </div>
  );
}

function ContactStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-5">
      <div className={grid2}>
        <Input ltr type="tel" label={T("Phone")} value={d.phone} onChange={(phone) => set({ phone })} />
        <Input ltr type="email" label={T("Email")} value={d.email} onChange={(email) => set({ email })} />
      </div>
      <Input label={T("Address")} value={d.address} onChange={(address) => set({ address })} placeholder={T("Street, city")} />
      <fieldset>
        <legend className="field-label mb-1.5">{T("Opening hours")}</legend>
        <ItemList T={T} items={d.hours} onChange={(hours) => set({ hours })} make={blank.hours} addLabel={T("Add another")}
          render={(h, up) => (
            <div className="grid grid-cols-[1fr_5.5rem_5.5rem] items-end gap-2">
              <Input label={T("Days")} value={h.label} onChange={(label) => up({ label })} placeholder={T("Mon–Fri")} />
              <Input ltr type="time" label={T("Opens")} value={h.open} onChange={(open) => up({ open })} />
              <Input ltr type="time" label={T("Closes")} value={h.close} onChange={(close) => up({ close })} />
            </div>
          )} />
      </fieldset>
      <fieldset>
        <legend className="field-label mb-1.5">{T("Social links (optional)")}</legend>
        <div className={grid2}>
          {SOCIALS.map((k) => (
            <Input key={k} ltr label={k[0].toUpperCase() + k.slice(1)} value={d.social[k] ?? ""} placeholder="https://"
              onChange={(v) => set({ social: { ...d.social, [k]: v } })} />
          ))}
        </div>
      </fieldset>
    </div>
  );
}

export const PAGE_INFO: Record<PageKind, [string, string]> = {
  about: ["About", "Your story and who you are."],
  services: ["Services", "What you offer, with prices if you like."],
  pricing: ["Pricing", "Plans or packages side by side."],
  team: ["Team", "The people behind the business."],
  faq: ["FAQ", "Answers to common questions."],
};

function PagesStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-2 sm:grid-cols-2">
        {PAGE_ORDER.map((k) => (
          <Choice key={k} type="checkbox" checked={d.pages.includes(k)} title={T(PAGE_INFO[k][0])} hint={T(PAGE_INFO[k][1])}
            onChange={() => set({ pages: d.pages.includes(k) ? d.pages.filter((x) => x !== k) : [...d.pages, k] })} />
        ))}
      </div>
      <p className="text-[12px] text-ink-500">{T("Home and Contact are always included. You can add more pages later in the editor.")}</p>
    </div>
  );
}

function HomeStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-5">
      <Input autoFocus label={T("Main headline")} value={d.headline} onChange={(headline) => set({ headline })} placeholder={d.tagline || T("Fresh bread, baked every morning")} />
      <Area rows={2} label={T("Line under the headline")} value={d.subheading} onChange={(subheading) => set({ subheading })} placeholder={d.description} />
      <fieldset>
        <legend className="field-label mb-1.5">{T("Why choose you? Up to three points")}</legend>
        <ItemList T={T} items={d.highlights} onChange={(highlights) => set({ highlights })} make={blank.highlight} addLabel={T("Add another")}
          render={(h, up) => (<>
            <Input label={T("Title")} value={h.title} onChange={(title) => up({ title })} placeholder={T("Made fresh")} />
            <Input label={T("Text")} value={h.text} onChange={(text) => up({ text })} />
          </>)} />
      </fieldset>
    </div>
  );
}

function ProofStep({ d, set, T }: StepProps) {
  return (
    <div className="space-y-5">
      <fieldset>
        <legend className="field-label mb-1.5">{T("Numbers you're proud of")}</legend>
        <ItemList T={T} items={d.stats} onChange={(stats) => set({ stats })} make={blank.stat} addLabel={T("Add another")}
          render={(s, up) => (
            <div className="grid grid-cols-[6rem_1fr] gap-2">
              <Input label={T("Number")} value={s.value} onChange={(value) => up({ value })} placeholder="10+" />
              <Input label={T("What it counts")} value={s.label} onChange={(label) => up({ label })} placeholder={T("Years in business")} />
            </div>
          )} />
      </fieldset>
      <fieldset>
        <legend className="field-label mb-1.5">{T("What customers say")}</legend>
        <ItemList T={T} items={d.testimonials} onChange={(testimonials) => set({ testimonials })} make={blank.quote} addLabel={T("Add another")}
          render={(q, up) => (<>
            <Area rows={2} label={T("Quote")} value={q.quote} onChange={(quote) => up({ quote })} />
            <div className={grid2}>
              <Input label={T("Name")} value={q.author} onChange={(author) => up({ author })} />
              <Input label={T("Role")} value={q.role} onChange={(role) => up({ role })} />
            </div>
          </>)} />
      </fieldset>
    </div>
  );
}

function AboutStep({ d, set, T }: StepProps) {
  return <Area rows={9} label={T("Your story")} value={d.story} onChange={(story) => set({ story })} placeholder={T("How you started, what you care about, who you help.")} />;
}

function ServicesStep({ d, set, T }: StepProps) {
  return (
    <ItemList T={T} items={d.services} onChange={(services) => set({ services })} make={blank.service} addLabel={T("Add another")}
      render={(s, up) => (<>
        <div className="grid grid-cols-[1fr_6rem] gap-2">
          <Input label={T("Name")} value={s.title} onChange={(title) => up({ title })} placeholder={T("Sourdough loaf")} />
          <Input label={T("Price")} value={s.price} onChange={(price) => up({ price })} />
        </div>
        <Input label={T("Short description")} value={s.description} onChange={(description) => up({ description })} />
      </>)} />
  );
}

function PricingStep({ d, set, T }: StepProps) {
  return (
    <ItemList T={T} items={d.plans} onChange={(plans) => set({ plans })} make={blank.plan} addLabel={T("Add another")}
      render={(p, up) => (<>
        <div className="grid grid-cols-[1fr_6rem_7rem] gap-2">
          <Input label={T("Plan name")} value={p.name} onChange={(name) => up({ name })} />
          <Input label={T("Price")} value={p.price} onChange={(price) => up({ price })} />
          <Input label={T("Per")} value={p.period} onChange={(period) => up({ period })} placeholder={T("month")} />
        </div>
        <Area rows={3} label={T("What's included (one per line)")} value={p.features} onChange={(features) => up({ features })} />
        <label className="flex items-center gap-2 text-[13px]">
          <input type="checkbox" checked={p.highlighted} onChange={(e) => up({ highlighted: e.target.checked })} />{T("Highlight as the favourite")}
        </label>
      </>)} />
  );
}

function TeamStep({ d, set, T }: StepProps) {
  return (
    <ItemList T={T} items={d.team} onChange={(team) => set({ team })} make={blank.member} addLabel={T("Add another")}
      render={(m, up) => (<>
        <div className={grid2}>
          <Input label={T("Name")} value={m.name} onChange={(name) => up({ name })} />
          <Input label={T("Role")} value={m.role} onChange={(role) => up({ role })} />
        </div>
        <Area rows={2} label={T("A line about them")} value={m.bio} onChange={(bio) => up({ bio })} />
      </>)} />
  );
}

function FaqStep({ d, set, T }: StepProps) {
  return (
    <ItemList T={T} items={d.faq} onChange={(faq) => set({ faq })} make={blank.faq} addLabel={T("Add another")}
      render={(f, up) => (<>
        <Input label={T("Question")} value={f.question} onChange={(question) => up({ question })} />
        <Area rows={2} label={T("Answer")} value={f.answer} onChange={(answer) => up({ answer })} />
      </>)} />
  );
}

function LookStep({ d, set, T }: StepProps) {
  const templates = useTemplates().data ?? [];
  const chosen = d.template ?? STARTER_FOR_TYPE[d.business_type];
  const palette = templates.find((x) => x.id === chosen)?.theme.palette;
  return (
    <div className="space-y-5">
      <fieldset>
        <legend className="field-label mb-1.5">{T("Style")}</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          {templates.map((tpl) => (
            <Choice key={tpl.id} type="radio" name="template" checked={chosen === tpl.id} onChange={() => set({ template: tpl.id, primary: null, accent: null })}
              title={T(tpl.label)} hint={T(tpl.description)}>
              <div className="mb-2"><Swatches palette={tpl.theme.palette} /></div>
            </Choice>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="field-label mb-1.5">{T("Your colours (optional)")}</legend>
        <div className="flex flex-wrap items-center gap-4 text-[13px]">
          {(["primary", "accent"] as const).map((k) => (
            <label key={k} className="flex items-center gap-2">
              <input type="color" value={d[k] ?? palette?.[k] ?? "#2563EB"} onChange={(e) => set({ [k]: e.target.value })} className="h-8 w-10 cursor-pointer rounded border border-ink-300 bg-white p-0.5" />
              {k === "primary" ? T("Main colour") : T("Accent colour")}
            </label>
          ))}
          {(d.primary || d.accent) && <Button type="button" variant="quiet" onClick={() => set({ primary: null, accent: null })}>{T("Use the style's colours")}</Button>}
        </div>
      </fieldset>
      <p className="text-[12px] text-ink-500">{T("You can add photos and fine-tune everything in the editor next.")}</p>
    </div>
  );
}

/* ---------- registry ---------- */

export const STEP_VIEW: Record<StepId, { title: string; help: string; optional?: boolean; View: (p: StepProps) => ReactNode }> = {
  language: { title: "Which language is your site in?", help: "The form and your site's starting text will use it.", View: LanguageStep },
  business: { title: "Tell us about your business", help: "We'll use this across the whole site.", View: BusinessStep },
  goal: { title: "What should visitors do?", help: "This becomes the main button on your home page.", View: GoalStep },
  contact: { title: "How can people reach you?", help: "Shown on your contact page and in the footer.", optional: true, View: ContactStep },
  pages: { title: "Which pages do you need?", help: "Pick the pages to add next to Home and Contact.", View: PagesStep },
  home: { title: "Your home page", help: "The first thing visitors read.", optional: true, View: HomeStep },
  proof: { title: "Numbers and reviews", help: "Leave this empty and we'll leave it off the site.", optional: true, View: ProofStep },
  about: { title: "About page", help: "Tell your story in your own words.", optional: true, View: AboutStep },
  services: { title: "Services page", help: "Add what you offer. Prices are optional.", optional: true, View: ServicesStep },
  pricing: { title: "Pricing page", help: "Add your plans or packages.", optional: true, View: PricingStep },
  team: { title: "Team page", help: "Add the people visitors will meet.", optional: true, View: TeamStep },
  faq: { title: "FAQ page", help: "Answer the questions you hear most.", optional: true, View: FaqStep },
  look: { title: "Pick a look", help: "Choose a style, then adjust the colours if you like.", View: LookStep },
};
