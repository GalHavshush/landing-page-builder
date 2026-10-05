/** One place for icons so the whole UI shares stroke weight and size. */
import {
  ArrowLeft, ArrowUpRight, Check, ChevronDown, ChevronRight, Copy, Download, FileText, GripVertical, Image as ImageIcon,
  LayoutGrid, Link as LinkIcon, List, Map as MapIcon, Megaphone, Monitor, MessageSquareQuote, Newspaper, Play, Plus, Quote,
  Redo2, Smartphone, Sparkles, Tags, Trash2, Type, Undo2, X, Users, HelpCircle, Mail, Rows3, Share2, Globe,
  Clock, BarChart3, Building2, ListOrdered, MousePointerClick, MoveHorizontal,
} from "lucide-react";
import type { LucideProps } from "lucide-react";

const base = { size: 16, strokeWidth: 1.6 } as const;
const wrap = (Cmp: React.ComponentType<LucideProps>) => (p: LucideProps) => <Cmp {...base} {...p} />;

export const IconBack = wrap(ArrowLeft);
export const IconCheck = wrap(Check);
export const IconChevronDown = wrap(ChevronDown);
export const IconChevronRight = wrap(ChevronRight);
export const IconCopy = wrap(Copy);
export const IconDownload = wrap(Download);
export const IconGrip = wrap(GripVertical);
export const IconPlus = wrap(Plus);
export const IconRedo = wrap(Redo2);
export const IconUndo = wrap(Undo2);
export const IconTrash = wrap(Trash2);
export const IconClose = wrap(X);
export const IconDesktop = wrap(Monitor);
export const IconMobile = wrap(Smartphone);
export const IconShare = wrap(Share2);
export const IconExternal = wrap(ArrowUpRight);
export const IconGlobe = wrap(Globe);

/** An icon for each section type, used in the section list and the "add section" picker. */
const SECTION_ICONS: Record<string, React.ComponentType<LucideProps>> = {
  hero: Megaphone, text: Type, features: Sparkles, services: Tags, gallery: ImageIcon, testimonials: MessageSquareQuote,
  pricing: LayoutGrid, faq: HelpCircle, contact: Mail, youtube: Play, map: MapIcon, blog_list: Newspaper,
  team: Users, hours: Clock, stats: BarChart3, logos: Building2, steps: ListOrdered, cta: MousePointerClick,
  compare: MoveHorizontal,
};
export function SectionIcon({ type, ...p }: LucideProps & { type: string }) {
  const Cmp = SECTION_ICONS[type] ?? Rows3;
  return <Cmp {...base} {...p} />;
}
export const IconPage = wrap(FileText);
export const IconList = wrap(List);
export const IconLink = wrap(LinkIcon);
export const IconQuote = wrap(Quote);
export const IconUsers = wrap(Users);
