import { ApiError } from "@/api/client";
import type { SiteDocument } from "@/api/types";
import { useEditor } from "./store";

export type SaveFn = (doc: SiteDocument, baseRevision: number) => Promise<{ revision: number }>;

/**
 * Saves the document shortly after edits stop.
 *  - Only one request in flight; edits made meanwhile trigger a follow-up save.
 *  - 409 (someone else saved first) stops saving and tells the user; we never overwrite.
 *  - 422 (server says the document is invalid) stops until the next edit.
 *  - Network errors retry with exponential backoff.
 */
export class Autosaver {
  private timer: ReturnType<typeof setTimeout> | undefined;
  private inFlight = false;
  private failures = 0;
  private unsubscribe: (() => void) | undefined;

  constructor(
    private save: SaveFn,
    private delay = 800,
  ) {}

  start() {
    let lastDoc = useEditor.getState().doc;
    this.unsubscribe = useEditor.subscribe((s) => {
      if (s.doc !== lastDoc) {
        lastDoc = s.doc;
        const { doc, savedDoc, saveStatus } = s;
        if (doc && doc !== savedDoc && saveStatus !== "conflict") this.schedule(this.delay);
      }
    });
  }

  stop() {
    this.unsubscribe?.();
    clearTimeout(this.timer);
  }

  private schedule(ms: number) {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => void this.flush(), ms);
  }

  /** Save now (used before export and on unload). */
  async flush(): Promise<void> {
    clearTimeout(this.timer);
    const state = useEditor.getState();
    if (this.inFlight || !state.doc || state.doc === state.savedDoc || state.saveStatus === "conflict") return;
    const sending = state.doc;
    this.inFlight = true;
    state.setSave("saving");
    try {
      const { revision } = await this.save(sending, state.revision);
      this.failures = 0;
      useEditor.getState().markSaved(sending, revision);
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        useEditor.getState().setSave("conflict", "This site was changed somewhere else.");
        this.inFlight = false;
        return;
      }
      if (e instanceof ApiError && e.status === 422) {
        useEditor.getState().setSave("invalid", "The server rejected these changes.");
        this.inFlight = false;
        return;
      }
      this.failures += 1;
      useEditor.getState().setSave("error", "Could not save. Retrying…");
      this.schedule(Math.min(30_000, 2000 * 2 ** (this.failures - 1)));
      this.inFlight = false;
      return;
    }
    this.inFlight = false;
    const after = useEditor.getState();
    if (after.doc !== after.savedDoc) this.schedule(this.delay); // edited while saving
  }
}
