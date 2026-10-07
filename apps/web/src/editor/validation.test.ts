import { describe, expect, it } from "vitest";
import { isEmail, isHttpsUrl } from "./validation";

describe("isEmail", () => {
  it.each(["a@b.co", " carl@example.com "])("accepts %s", (v) => expect(isEmail(v)).toBe(true));
  it.each(["", "bad-email", "a@b", "@x.com", "x@", "two words@x.com"])("rejects %j", (v) => expect(isEmail(v)).toBe(false));
});

describe("isHttpsUrl", () => {
  it.each(["https://example.com", "https://example.com/path"])("accepts %s", (v) => expect(isHttpsUrl(v)).toBe(true));
  it.each(["http://example.com", "example.com", "https://", "javascript:alert(1)", "https://a b.com"])("rejects %s", (v) => expect(isHttpsUrl(v)).toBe(false));
});
