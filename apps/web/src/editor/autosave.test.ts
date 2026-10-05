import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/api/client";
import type { SiteDocument } from "@/api/types";
import { Autosaver } from "./autosave";
import * as c from "./commands";
import { useEditor } from "./store";

const sec = (id: string) =>
  ({ id, type: "text", variant: "single", style: {}, i18n: {}, props: { heading: id, body: "" } }) as never;
const base = () =>
  ({
    schema_version: 1,
    site: { name: "T", nav: [], default_language: "en", languages: ["en"] },
    theme: {},
    pages: [{ id: "p1", slug: "", title: "Home", seo: {}, i18n: {}, sections: [sec("a")] }],
  }) as unknown as SiteDocument;

let saver: Autosaver;
beforeEach(() => {
  vi.useFakeTimers();
  useEditor.getState().load(1, base(), 1);
});
afterEach(() => {
  saver.stop();
  vi.useRealTimers();
});

const edit = (text: string) => useEditor.getState().apply(c.updateProps("a", { heading: text }));
const status = () => useEditor.getState().saveStatus;

describe("Autosaver", () => {
  it("saves once after edits stop, with the base revision", async () => {
    const save = vi.fn().mockResolvedValue({ revision: 2 });
    saver = new Autosaver(save, 500);
    saver.start();
    edit("1");
    edit("2");
    await vi.advanceTimersByTimeAsync(499);
    expect(save).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(2);
    expect(save).toHaveBeenCalledTimes(1);
    expect(save.mock.calls[0][1]).toBe(1);
    expect(status()).toBe("saved");
    expect(useEditor.getState().revision).toBe(2);
  });

  it("saves again if edited while a save is in flight", async () => {
    let release!: (v: { revision: number }) => void;
    const save = vi
      .fn()
      .mockImplementationOnce(() => new Promise((r) => (release = r)))
      .mockResolvedValue({ revision: 3 });
    saver = new Autosaver(save, 100);
    saver.start();
    edit("1");
    await vi.advanceTimersByTimeAsync(101);
    expect(status()).toBe("saving");
    edit("2"); // during the request
    release({ revision: 2 });
    await vi.advanceTimersByTimeAsync(0);
    expect(status()).toBe("dirty");
    await vi.advanceTimersByTimeAsync(101);
    expect(save).toHaveBeenCalledTimes(2);
    expect(save.mock.calls[1][1]).toBe(2); // uses the new revision
    expect(status()).toBe("saved");
  });

  it("stops on a 409 conflict and never overwrites", async () => {
    const save = vi.fn().mockRejectedValue(new ApiError(409, "conflict"));
    saver = new Autosaver(save, 100);
    saver.start();
    edit("1");
    await vi.advanceTimersByTimeAsync(101);
    expect(status()).toBe("conflict");
    edit("2");
    await vi.advanceTimersByTimeAsync(5000);
    expect(save).toHaveBeenCalledTimes(1);
  });

  it("retries network errors with backoff", async () => {
    const save = vi.fn().mockRejectedValueOnce(new TypeError("offline")).mockResolvedValue({ revision: 2 });
    saver = new Autosaver(save, 100);
    saver.start();
    edit("1");
    await vi.advanceTimersByTimeAsync(101);
    expect(status()).toBe("error");
    await vi.advanceTimersByTimeAsync(2001);
    expect(save).toHaveBeenCalledTimes(2);
    expect(status()).toBe("saved");
  });

  it("marks invalid documents and waits for the next edit", async () => {
    const save = vi.fn().mockRejectedValue(new ApiError(422, []));
    saver = new Autosaver(save, 100);
    saver.start();
    edit("1");
    await vi.advanceTimersByTimeAsync(101);
    expect(status()).toBe("invalid");
    await vi.advanceTimersByTimeAsync(10_000);
    expect(save).toHaveBeenCalledTimes(1);
    edit("2");
    await vi.advanceTimersByTimeAsync(101);
    expect(save).toHaveBeenCalledTimes(2);
  });
});
