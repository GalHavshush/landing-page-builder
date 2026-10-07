import { useState } from "react";
import type { EditorMeta, PropSchema, Section, SectionMeta } from "@/api/types";
import { setVariant, setTranslation, updateProps, updateStyle } from "./commands";
import { fieldLabel } from "./labels";
import { SectionIcon } from "@/components/icons";
import { SegmentedControl } from "./controls/basic";
import { Control, type Env } from "./controls/registry";
import { SettingsPanel } from "./SettingsPanel";
import { currentPage, useCanEditStructure, useEditor } from "./store";

const humanize = fieldLabel;
const enumOptions = (values: (string | number)[]) => values.map((v) => ({ value: v, label: String(v) }));

/** Where the editor reads/writes a prop: the section itself, or a translation overlay. */
interface FieldCtx {
  section: Section;
  lang: string;
  defaultLang: string;
}

function PropField({ name, schema, ctx, env }: { name: string; schema: PropSchema; ctx: FieldCtx; env: Env }) {
  const apply = useEditor((s) => s.apply);
  const { section, lang, defaultLang } = ctx;
  const translating = lang !== defaultLang && schema.group === "content";
  const props = section.props as unknown as Record<string, unknown>;
  const base = props[name];
  const override = section.i18n[lang]?.[name];
  const isText = ["text", "textarea", "richtext"].includes(schema.control as string);

  if (lang !== defaultLang && schema.group === "design") return null; // structure is shared

  const write = (value: unknown, typing?: boolean) => {
    const key = typing ? `${section.id}.${name}.${lang}` : undefined;
    if (translating) {
      // clearing a translated text falls back to the default language
      apply(setTranslation(section.id, lang, name, value === "" ? undefined : value), { coalesceKey: key });
    } else {
      apply(updateProps(section.id, { [name]: value }), { coalesceKey: key });
    }
  };

  if (translating && isText) {
    return (
      <Control name={name} schema={schema} env={env} value={(override as string | undefined) ?? ""}
        placeholder={base as string} onChange={write}
        hint={override === undefined ? "Not translated yet: showing the default language." : undefined} />
    );
  }
  if (translating) {
    // lists, links, images: a translation replaces the whole value
    return (
      <div className="space-y-1">
        <Control name={name} schema={schema} env={env} value={override ?? base} onChange={write} />
        <p className="text-xs text-ink-500">
          {override === undefined ? "Using the default language." : "Translated."}
          {override !== undefined && (
            <button className="ml-2 text-ink-700 underline decoration-ink-300 underline-offset-2 hover:decoration-ink-900" onClick={() => apply(setTranslation(section.id, lang, name, undefined))}>
              Reset to default
            </button>
          )}
        </p>
      </div>
    );
  }
  return <Control name={name} schema={schema} env={env} value={base} onChange={write} />;
}

function StyleFields({ section, meta }: { section: Section; meta: EditorMeta }) {
  const apply = useEditor((s) => s.apply);
  const styleProps = meta.section_style_schema.properties;
  return (
    <div className="space-y-3">
      {(["background", "spacing", "align"] as const).map((key) => (
        <SegmentedControl
          key={key}
          label={humanize(key)}
          value={section.style[key] as string}
          options={enumOptions(styleProps[key].enum ?? [])}
          onChange={(v) => apply(updateStyle(section.id, { [key]: v }))}
        />
      ))}
    </div>
  );
}

export function PropertiesPanel({ meta }: { meta: EditorMeta }) {
  const doc = useEditor((s) => s.doc)!;
  const page = useEditor(currentPage);
  const selectedId = useEditor((s) => s.selectedId);
  const lang = useEditor((s) => s.lang)!;
  const defaultLang = useEditor((s) => s.doc!.site.default_language);
  const apply = useEditor((s) => s.apply);
  const [pickedTab, setTab] = useState<"content" | "design">("content");
  const canEdit = useCanEditStructure();
  const tab = canEdit ? pickedTab : "content";
  const section = page?.sections.find((s) => s.id === selectedId);

  if (!section) return <SettingsPanel meta={meta} />;
  const sectionMeta: SectionMeta | undefined = meta.sections.find((m) => m.type === section.type);
  const entries = Object.entries(sectionMeta?.props_schema.properties ?? {});
  const content = entries.filter(([, s]) => s.group === "content");
  const design = entries.filter(([, s]) => s.group === "design");
  const ctx: FieldCtx = { section, lang, defaultLang };
  const env: Env = {
    meta,
    pages: doc.pages.map((p) => ({ id: p.id, title: p.title })),
    defs: (sectionMeta?.props_schema.$defs ?? {}) as Env["defs"],
  };
  const translating = lang !== defaultLang;

  return (
    <aside aria-label="Section settings" className="flex min-h-0 flex-col border-l border-ink-200 bg-white">
      <div className="border-b border-ink-200 px-4 pt-3.5">
        <h2 className="flex items-center gap-2 text-[13px] font-semibold tracking-tight">
          <span className="grid h-5 w-5 place-items-center rounded bg-ink-100 text-ink-700"><SectionIcon type={section.type} size={12} /></span>
          {sectionMeta?.label ?? section.type}
        </h2>
        {translating && <p className="mt-0.5 text-[12px] text-ink-600">Translating to {meta.languages[lang] ?? lang}</p>}
        <div role="tablist" className="mt-2.5 flex gap-4">
          {(canEdit ? (["content", "design"] as const) : (["content"] as const)).map((t) => (
            <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
              className={`-mb-px border-b-[1.5px] py-2 text-[13px] font-medium capitalize transition ${tab === t ? "border-ink-900 text-ink-900" : "border-transparent text-ink-500 hover:text-ink-800"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        {tab === "content" && content.map(([name, schema]) => <PropField key={`${section.id}.${name}`} name={name} schema={schema} ctx={ctx} env={env} />)}
        {tab === "design" &&
          (translating ? (
            <p className="text-sm text-ink-500">Design is shared by all languages. Switch back to the default language to change it.</p>
          ) : (
            <>
              {sectionMeta && sectionMeta.variants.length > 1 && (
                <SegmentedControl
                  label="Layout"
                  value={section.variant}
                  options={sectionMeta.variants.map((v) => ({ value: v, label: v }))}
                  onChange={(v) => apply(setVariant(section.id, v))}
                />
              )}
              <StyleFields section={section} meta={meta} />
              {design.map(([name, schema]) => <PropField key={`${section.id}.${name}`} name={name} schema={schema} ctx={ctx} env={env} />)}
            </>
          ))}
      </div>
    </aside>
  );
}
