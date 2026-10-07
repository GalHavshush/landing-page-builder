import { describe, expect, it } from "vitest";
import { fieldLabel } from "./labels";

describe("fieldLabel", () => {
  it("replaces developer words", () => {
    expect(fieldLabel("href")).toBe("Link");
    expect(fieldLabel("video_url")).toBe("Video link (YouTube)");
    expect(fieldLabel("show_business_info")).toBe("Show business details");
  });
  it("uses sentence case for everything else", () => {
    expect(fieldLabel("before_label")).toBe("Before label");
    expect(fieldLabel("heading")).toBe("Heading");
  });
});
