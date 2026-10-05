/** Thin fetch wrapper: same-origin cookie auth + the CSRF header the API requires. */

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(typeof detail === "string" ? detail : `Request failed (${status})`);
  }
}

export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown; form?: FormData; raw?: boolean; signal?: AbortSignal } = {},
): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method: options.method ?? "GET",
    credentials: "include",
    signal: options.signal,
    headers: {
      "X-Requested-With": "builder",
      // for FormData the browser sets the multipart Content-Type (with boundary) itself
      ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    body: options.form ?? (options.body !== undefined ? JSON.stringify(options.body) : undefined),
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* not JSON */
    }
    throw new ApiError(res.status, detail);
  }
  if (options.raw) return res as unknown as T;
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
