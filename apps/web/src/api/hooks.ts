import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "./client";
import type { Asset, PostIn, PostOut, EditorMeta, Project, SiteDocument, User } from "./types";

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

export const useAssets = (projectId: number) =>
  useQuery({ queryKey: ["assets", projectId], queryFn: () => api<Asset[]>(`/projects/${projectId}/assets`) });

export function useUploadAsset(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return api<Asset>(`/projects/${projectId}/assets`, { method: "POST", form });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets", projectId] }),
  });
}

export function useDeleteAsset(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (assetId: string) => api<void>(`/projects/${projectId}/assets/${assetId}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets", projectId] }),
  });
}

export const usePosts = (projectId: number) =>
  useQuery({ queryKey: ["posts", projectId], queryFn: () => api<PostOut[]>(`/projects/${projectId}/posts`) });

export function usePostMutations(projectId: number) {
  const qc = useQueryClient();
  const refresh = () => qc.invalidateQueries({ queryKey: ["posts", projectId] });
  return {
    create: useMutation({
      mutationFn: (body: PostIn) => api<PostOut>(`/projects/${projectId}/posts`, { method: "POST", body }),
      onSuccess: refresh,
    }),
    save: useMutation({
      mutationFn: ({ id, body }: { id: string; body: PostIn }) =>
        api<PostOut>(`/projects/${projectId}/posts/${id}`, { method: "PUT", body }),
      // no refresh here: the editor owns the text while it is open; the list is refreshed on close
    }),
    remove: useMutation({
      mutationFn: (id: string) => api<void>(`/projects/${projectId}/posts/${id}`, { method: "DELETE" }),
      onSuccess: refresh,
    }),
    translate: useMutation({
      mutationFn: ({ id, lang }: { id: string; lang: string }) =>
        api<PostOut>(`/projects/${projectId}/posts/${id}/translate`, { method: "POST", body: { lang } }),
      onSuccess: refresh,
    }),
  };
}
