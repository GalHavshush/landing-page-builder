import { useState } from "react";
import type { EditorMeta, PropSchema, Section, SectionMeta } from "@/api/types";
import { setVariant, setTranslation, updateProps, updateStyle } from "./commands";
import { SegmentedControl, SelectControl, TextAreaControl, TextControl, ToggleControl } from "./controls/basic";
import { currentPage, useEditor } from "./store";

const humanize = (s: string) => s.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
const enumOptions = (values: (string | number)[]) => values.map((v) => ({ value: v, label: String(v) }));

/** Where the editor reads/writes a prop: the section itself, or a translation overlay. */
interface FieldCtx {
  section: Section;
  lang: string;
  defaultLang: string;
}

function PropField({ name, schema, ctx }: { name: string; schema: PropSchema; ctx: FieldCtx }) {
  const apply = useEditor((s) => s.apply);
  const { section, lang, defaultLang } = ctx;
  const translating = lang !== defaultLang && schema.group === "content";
  const props = section.props as unknown as Record<string, unknown>;
  const base = props[name];
  const override = section.i18n[lang]?.[name];
  const label = schema.title ?? humanize(name);
  const control = schema.control;

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

  if (control === "text" || control === "textarea" || control === "richtext") {
    const shown = translating ? ((override as string | undefined) ?? "") : (base as string);
    const placeholder = translating ? (base as string) : undefined;
    const hint = control === "richtext" ? "Supports Markdown: **bold**, *italic*, lists, [links](https://…)" : translating && override === undefined ? "Not translated yet: showing the default language." : undefined;
    return control === "text" ? (
      <TextControl label={label} value={shown} onChange={write} placeholder={placeholder} hint={hint} />
    ) : (
      <TextAreaControl label={label} value={shown} onChange={write} placeholder={placeholder} hint={hint} rows={control === "richtext" ? 8 : 3} />
    );
  }
  if (control === "segmented" || control === "select") {
    const options = enumOptions(schema.enum ?? []);
    const Cmp = control === "segmented" && options.length <= 4 ? SegmentedControl : SelectControl;
    return <Cmp label={label} value={base as string | number} options={options} onChange={(v) => write(v)} />;
  }
  if (control === "toggle" || schema.type === "boolean") {
    return <ToggleControl label={label} value={Boolean(base)} onChange={(v) => write(v)} />;
  }
  return (
    <p className="rounded bg-slate-50 px-2 py-1.5 text-xs text-slate-500">
      {label}: editor for “{control}” fields arrives in the next step.
    </p>
  );
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
  const page = useEditor(currentPage);
  const selectedId = useEditor((s) => s.selectedId);
  const lang = useEditor((s) => s.lang)!;
  const defaultLang = useEditor((s) => s.doc!.site.default_language);
  const apply = useEditor((s) => s.apply);
  const [tab, setTab] = useState<"content" | "design">("content");
  const section = page?.sections.find((s) => s.id === selectedId);

  if (!section) {
    return (
      <aside className="min-h-0 overflow-y-auto border-l border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-500">Select a section in the list or in the preview to edit it.</p>
      </aside>
    );
  }
  const sectionMeta: SectionMeta | undefined = meta.sections.find((m) => m.type === section.type);
  const entries = Object.entries(sectionMeta?.props_schema.properties ?? {});
  const content = entries.filter(([, s]) => s.group === "content");
  const design = entries.filter(([, s]) => s.group === "design");
  const ctx: FieldCtx = { section, lang, defaultLang };
  const translating = lang !== defaultLang;

  return (
    <aside className="flex min-h-0 flex-col border-l border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-4 pt-3">
        <h2 className="text-sm font-semibold">{sectionMeta?.label ?? section.type}</h2>
        {translating && <p className="mt-0.5 text-xs text-indigo-600">Translating to {meta.languages[lang] ?? lang}</p>}
        <div role="tablist" className="mt-2 flex gap-4">
          {(["content", "design"] as const).map((t) => (
            <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
              className={`-mb-px border-b-2 pb-2 text-sm capitalize ${tab === t ? "border-indigo-600 font-medium text-indigo-700" : "border-transparent text-slate-500 hover:text-slate-800"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        {tab === "content" && content.map(([name, schema]) => <PropField key={`${section.id}.${name}`} name={name} schema={schema} ctx={ctx} />)}
        {tab === "design" &&
          (translating ? (
            <p className="text-sm text-slate-500">Design is shared by all languages. Switch back to the default language to change it.</p>
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
              {design.map(([name, schema]) => <PropField key={`${section.id}.${name}`} name={name} schema={schema} ctx={ctx} />)}
            </>
          ))}
      </div>
    </aside>
  );
}
