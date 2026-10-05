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
import { IconCopy, IconGrip, IconTrash, SectionIcon } from "@/components/icons";
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
  const tool = "grid h-6 w-6 place-items-center rounded text-ink-500 transition hover:bg-ink-200/70 hover:text-ink-900";

  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`group relative flex items-center rounded-md transition-colors ${
        selected ? "bg-ink-100" : "hover:bg-ink-100/70"
      } ${isDragging ? "z-10 bg-white shadow-pop ring-1 ring-ink-200" : ""}`}
    >
      {selected && <span className="absolute inset-y-1.5 left-0 w-[2px] rounded-full bg-accent-500" />}
      {canEdit ? (
        <button aria-label={`Drag ${label}`} {...attributes} {...listeners}
          className="grid h-8 w-5 shrink-0 cursor-grab touch-none place-items-center text-ink-300 transition hover:text-ink-600 active:cursor-grabbing group-hover:text-ink-500">
          <IconGrip size={14} />
        </button>
      ) : (
        <span className="w-2" />
      )}
      <button onClick={() => selectSection(section.id)} className="flex min-w-0 flex-1 items-center gap-2.5 py-1.5 pr-1 text-left">
        <span className={`grid h-6 w-6 shrink-0 place-items-center rounded ${selected ? "bg-white text-ink-900 ring-1 ring-ink-200" : "text-ink-500"}`}>
          <SectionIcon type={section.type} size={14} />
        </span>
        <span className="min-w-0">
          <span className="block truncate text-[13px] font-medium leading-tight">{label}</span>
          <span className="block truncate text-[11.5px] leading-tight text-ink-500">{subtitle(section) || "Empty"}</span>
        </span>
      </button>
      {canEdit && (
        <div className="mr-1 flex items-center opacity-0 transition group-focus-within:opacity-100 group-hover:opacity-100">
          <button aria-label={`Duplicate ${label}`} title="Duplicate" className={tool} onClick={() => apply(duplicateSection(section.id))}>
            <IconCopy size={13} />
          </button>
          <button aria-label={`Delete ${label}`} title="Delete (you can undo)" className={`${tool} hover:!bg-red-600 hover:!text-white`} onClick={() => apply(removeSection(section.id))}>
            <IconTrash size={13} />
          </button>
        </div>
      )}
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
        <ul>
          {sections.map((s) => (
            <Item key={s.id} section={s} label={label(s.type)} />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  );
}
