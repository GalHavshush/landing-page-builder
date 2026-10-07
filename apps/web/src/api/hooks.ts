import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { getUiLang, setUiLang, type UiLang } from "@/i18n";
import { getThemePref, setThemePref, type ThemePref } from "@/theme";
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

/** Editor language and theme live on the account; apply them whenever the signed-in user loads. */
export function useApplyPreferences() {
  const me = useMe().data;
  useEffect(() => {
    if (!me) return;
    setUiLang(me.ui_language as UiLang);
    setThemePref(me.ui_theme as ThemePref);
  }, [me]);
}

export function useSavePreferences() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { ui_language?: UiLang; ui_theme?: ThemePref }) => api<User>("/auth/me", { method: "PATCH", body }),
    onSuccess: (user) => qc.setQueryData(["me"], user),
  });
}

export function useAuthMutation(kind: "login" | "register") {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { email: string; password: string; name?: string }) =>
      api<User>(`/auth/${kind}`, { method: "POST", body }),
    onSuccess: (user) => {
      if (kind === "login") return qc.setQueryData(["me"], user);
      // a new account starts with the language and theme chosen on the sign-in screen
      const prefs = { ui_language: getUiLang(), ui_theme: getThemePref() };
      qc.setQueryData(["me"], { ...user, ...prefs });
      void api("/auth/me", { method: "PATCH", body: prefs });
    },
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
  useQuery({ queryKey: ["templates"], queryFn: () => api<{ id: string; label: string; description: string; theme: { palette: Record<string, string> }; photo_hints: string[] }[]>("/templates") });

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; template: string; language: string; extra_languages: string[] }) =>
      api<Project>("/projects", { method: "POST", body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

/** `lang`: the language of the placeholder text for new sections and pages (the site's language). */
export const useEditorMeta = (lang?: string) =>
  useQuery({
    queryKey: ["editor-meta", lang ?? null],
    queryFn: () => api<EditorMeta>(`/editor-meta${lang ? `?lang=${lang}` : ""}`),
    staleTime: Infinity,
    placeholderData: keepPreviousData,
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

export interface Member {
  user_id: number;
  email: string;
  name: string;
  role: string;
}
export interface Invitation {
  id: number;
  role: string;
  email: string | null;
  expires_at: string;
}

export const useMembers = (projectId: number, enabled = true) =>
  useQuery({
    queryKey: ["members", projectId],
    enabled,
    queryFn: () => api<{ members: Member[]; invitations: Invitation[] }>(`/projects/${projectId}/members`),
  });

export function useMemberMutations(projectId: number) {
  const qc = useQueryClient();
  const refresh = () => qc.invalidateQueries({ queryKey: ["members", projectId] });
  return {
    invite: useMutation({
      mutationFn: (body: { role: "designer" | "editor"; email?: string }) =>
        api<Invitation & { token: string }>(`/projects/${projectId}/invitations`, { method: "POST", body }),
      onSuccess: refresh,
    }),
    revoke: useMutation({
      mutationFn: (id: number) => api<void>(`/projects/${projectId}/invitations/${id}`, { method: "DELETE" }),
      onSuccess: refresh,
    }),
    setRole: useMutation({
      mutationFn: ({ userId, role }: { userId: number; role: "designer" | "editor" }) =>
        api<Member>(`/projects/${projectId}/members/${userId}`, { method: "PATCH", body: { role } }),
      onSuccess: refresh,
    }),
    remove: useMutation({
      mutationFn: (userId: number) => api<void>(`/projects/${projectId}/members/${userId}`, { method: "DELETE" }),
      onSuccess: refresh,
    }),
  };
}

export const useInvitePreview = (token: string) =>
  useQuery({
    queryKey: ["invite", token],
    queryFn: () => api<{ project_name: string; role: string; email: string | null }>(`/invitations/${token}`),
  });

export function useAcceptInvite(token: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<{ project_id: number; role: string }>(`/invitations/${token}/accept`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export interface SiteExport {
  id: number;
  doc_revision: number;
  size_bytes: number;
  file_count: number;
  created_at: string;
  created_by: string;
  issues: { level: string; message: string; where: string }[];
}

export const useExports = (projectId: number, enabled = true) =>
  useQuery({
    queryKey: ["exports", projectId],
    enabled,
    queryFn: () => api<SiteExport[]>(`/projects/${projectId}/exports`),
  });

export function useCreateExport(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<SiteExport>(`/projects/${projectId}/exports`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["exports", projectId] }),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api<void>(`/projects/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export interface StockPhoto { id: string; thumb_url: string; width: number; height: number; alt: string; credit: string; page_url: string }
export interface StockSearch { enabled: boolean; provider: string; results: StockPhoto[] }

/** `q` empty only asks whether stock search is set up on this server. */
export const useStockSearch = (projectId: number, q: string) =>
  useQuery({
    queryKey: ["stock", projectId, q],
    queryFn: () => api<StockSearch>(`/projects/${projectId}/stock/search?q=${encodeURIComponent(q)}`),
    staleTime: 5 * 60_000,
  });

export function useImportStock(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (photoId: string) =>
      api<Asset>(`/projects/${projectId}/stock/import`, { method: "POST", body: { photo_id: photoId } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets", projectId] }),
  });
}
