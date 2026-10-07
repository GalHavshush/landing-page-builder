/** A tiny stand-in for a starter's look, drawn from its palette (no screenshots needed). */
export function Swatches({ palette }: { palette: Record<string, string> }) {
  return (
    <div className="flex h-9 overflow-hidden rounded-md ring-1 ring-inset ring-black/10" aria-hidden>
      <div className="flex-[3]" style={{ background: palette.background }}><div className="m-2 h-1.5 w-8 rounded-full" style={{ background: palette.text }} /><div className="mx-2 h-1 w-12 rounded-full opacity-40" style={{ background: palette.text }} /></div>
      <div className="flex-1" style={{ background: palette.primary }} />
      <div className="flex-1" style={{ background: palette.accent }} />
    </div>
  );
}
