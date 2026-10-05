import { QueryClient } from "@tanstack/react-query";

/** One shared client, so non-React code (e.g. the post editor's cache updates) can use it too. */
export const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
});
