import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "./client";
import type { EditorMeta, Project, SiteDocument, User } from "./types";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        return await api<User>("/auth/me");
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) return null;
        throw e;
      }
    },
    staleTime: 60_000,
  });
}

export function useAuthMutation(kind: "login" | "register") {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { email: string; password: string; name?: string }) =>
      api<User>(`/auth/${kind}`, { method: "POST", body }),
    onSuccess: (user) => qc.setQueryData(["me"], user),
  });
}

export function useLogout() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<void>("/auth/logout", { method: "POST" }),
    onSuccess: () => {
      qc.setQueryData(["me"], null);
      qc.removeQueries({ predicate: (q) => q.queryKey[0] !== "me" });
    },
  });
}

export const useProjects = () =>
  useQuery({ queryKey: ["projects"], queryFn: () => api<Project[]>("/projects") });

export const useTemplates = () =>
  useQuery({ queryKey: ["templates"], queryFn: () => api<string[]>("/templates") });

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; template: string }) =>
      api<Project>("/projects", { method: "POST", body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export const useEditorMeta = () =>
  useQuery({
    queryKey: ["editor-meta"],
    queryFn: () => api<EditorMeta>("/editor-meta"),
    staleTime: Infinity,
  });

export const useProject = (id: number) =>
  useQuery({ queryKey: ["project", id], queryFn: () => api<Project>(`/projects/${id}`) });

export const useDocument = (id: number) =>
  useQuery({
    queryKey: ["doc", id],
    queryFn: () => api<{ doc: SiteDocument; revision: number }>(`/projects/${id}/doc`),
    staleTime: Infinity, // the editor store owns the document once loaded
    gcTime: 0,
  });
