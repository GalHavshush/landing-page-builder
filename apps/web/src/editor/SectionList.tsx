import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { EditorMeta, Section } from "@/api/types";
import { duplicateSection, moveSection, removeSection } from "./commands";
import { useCanEditStructure, useEditor } from "./store";

function subtitle(s: Section): string {
  const p = s.props as unknown as Record<string, unknown>;
  return (((p.heading as string) || (p.eyebrow as string) || "") as string).slice(0, 40);
}

function Item({ section, label }: { section: Section; label: string }) {
  const selected = useEditor((s) => s.selectedId === section.id);
  const selectSection = useEditor((s) => s.selectSection);
  const apply = useEditor((s) => s.apply);
  const canEdit = useCanEditStructure();
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: section.id });

  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`group flex items-stretch rounded-md border bg-white ${
        selected ? "border-indigo-400 bg-indigo-50" : "border-slate-200 hover:border-slate-300"
      } ${isDragging ? "z-10 shadow-lg" : ""}`}
    >
      {canEdit ? (
        <button
          aria-label={`Drag ${label}`}
          className="cursor-grab touch-none px-1.5 text-slate-400 hover:text-slate-700 active:cursor-grabbing"
          {...attributes}
          {...listeners}
        >
          ⋮⋮
        </button>
      ) : (
        <span className="w-2" />
      )}
      <button onClick={() => selectSection(section.id)} className="min-w-0 flex-1 py-2 pr-1 text-left">
        <div className="text-sm font-medium">{label}</div>
        <div className="truncate text-xs text-slate-500">{subtitle(section) || "—"}</div>
      </button>
      {canEdit && <div className="flex items-center gap-0.5 pr-1 opacity-0 transition group-focus-within:opacity-100 group-hover:opacity-100">
        <button
          aria-label={`Duplicate ${label}`}
          title="Duplicate"
          className="rounded px-1.5 py-1 text-slate-500 hover:bg-slate-100"
          onClick={() => apply(duplicateSection(section.id))}
        >
          ⧉
        </button>
        <button
          aria-label={`Delete ${label}`}
          title="Delete (you can undo)"
          className="rounded px-1.5 py-1 text-slate-500 hover:bg-red-50 hover:text-red-600"
          onClick={() => apply(removeSection(section.id))}
        >
          ✕
        </button>
      </div>}
    </li>
  );
}

export function SectionList({ sections, meta }: { sections: Section[]; meta: EditorMeta }) {
  const apply = useEditor((s) => s.apply);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const label = (type: string) => meta.sections.find((m) => m.type === type)?.label ?? type;

  const onDragEnd = ({ active, over }: DragEndEvent) => {
    if (!over || active.id === over.id) return;
    const toIndex = sections.findIndex((s) => s.id === over.id);
    apply(moveSection(String(active.id), toIndex));
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
      <SortableContext items={sections.map((s) => s.id)} strategy={verticalListSortingStrategy}>
        <ul className="space-y-1">
          {sections.map((s) => (
            <Item key={s.id} section={s} label={label(s.type)} />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  );
}
