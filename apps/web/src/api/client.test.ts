import { describe, expect, it } from "vitest";
import { errorMessage } from "./client";

describe("errorMessage", () => {
  it("passes plain strings through", () => expect(errorMessage(409, "Taken")).toBe("Taken"));
  it("turns FastAPI validation lists into a sentence", () =>
    expect(errorMessage(422, [{ msg: "Value error, invalid email address", loc: ["body", "email"] }])).toBe("Invalid email address"));
  it("falls back to the status", () => expect(errorMessage(500, { weird: true })).toBe("Request failed (500)"));
});
