/** Small input checks shared by the settings fields. They mirror what the API accepts. */
export const isEmail = (v: string) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v.trim());
export const isHttpsUrl = (v: string) => /^https:\/\/[^\s/]+\.[^\s/]+/.test(v);
