/** Pure text edits for the Markdown toolbar. Each returns the new text and selection. */

export interface Edit {
  text: string;
  start: number;
  end: number;
}

/** Wrap the selection (or a placeholder) with `before`/`after`, e.g. **bold**. Toggles if already wrapped. */
export function wrap(text: string, start: number, end: number, before: string, after = before, placeholder = "text"): Edit {
  const selected = text.slice(start, end);
  const outerBefore = text.slice(start - before.length, start);
  const outerAfter = text.slice(end, end + after.length);
  if (selected && outerBefore === before && outerAfter === after) {
    // already wrapped: unwrap
    return { text: text.slice(0, start - before.length) + selected + text.slice(end + after.length), start: start - before.length, end: end - before.length };
  }
  const inner = selected || placeholder;
  const out = text.slice(0, start) + before + inner + after + text.slice(end);
  return { text: out, start: start + before.length, end: start + before.length + inner.length };
}

/** Add (or remove) a prefix on every line touched by the selection: "## ", "> ", "- ". */
export function prefixLines(text: string, start: number, end: number, prefix: string | ((i: number) => string)): Edit {
  const lineStart = text.lastIndexOf("\n", start - 1) + 1;
  const nl = text.indexOf("\n", end);
  const lineEnd = nl === -1 ? text.length : nl;
  const lines = text.slice(lineStart, lineEnd).split("\n");
  const pre = (i: number) => (typeof prefix === "function" ? prefix(i) : prefix);
  const allHave = lines.every((l, i) => l.startsWith(pre(i)));
  const next = lines.map((l, i) => (allHave ? l.slice(pre(i).length) : pre(i) + l.replace(/^(#{1,6} |> |- |\d+\. )/, "")));
  const block = next.join("\n");
  return { text: text.slice(0, lineStart) + block + text.slice(lineEnd), start: lineStart, end: lineStart + block.length };
}

export function insertAt(text: string, pos: number, snippet: string): Edit {
  const needsBreak = pos > 0 && text[pos - 1] !== "\n" ? "\n\n" : "";
  const insert = needsBreak + snippet + "\n";
  return { text: text.slice(0, pos) + insert + text.slice(pos), start: pos + insert.length, end: pos + insert.length };
}

export function makeLink(text: string, start: number, end: number, url = "https://"): Edit {
  const label = text.slice(start, end) || "link text";
  const md = `[${label}](${url})`;
  const out = text.slice(0, start) + md + text.slice(end);
  const urlStart = start + label.length + 3;
  return { text: out, start: urlStart, end: urlStart + url.length };
}
