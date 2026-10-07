import { useRef, useState } from "react";
import { useMemberMutations, useMembers } from "@/api/hooks";
import { IconShare } from "@/components/icons";
import { IconClose } from "@/components/icons";
import { Button } from "@/components/ui";

const ROLE_HELP: Record<string, string> = {
  designer: "Can change layout, design and all content.",
  editor: "Client: can change text, images, prices and posts, but not the design.",
};

/** Owner-only: who has access, and invite links for designers and clients. */
export function ShareDialog({ projectId }: { projectId: number }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const members = useMembers(projectId, open);
  const m = useMemberMutations(projectId);
  const [role, setRole] = useState<"designer" | "editor">("editor");
  const [email, setEmail] = useState("");
  const [link, setLink] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const show = () => {
    setOpen(true);
    dialog.current?.showModal();
  };
  const createInvite = () =>
    m.invite.mutate(
      { role, email: email.trim() || undefined },
      {
        onSuccess: (inv) => {
          setLink(`${window.location.origin}/invite/${inv.token}`);
          setCopied(false);
          setEmail("");
        },
      },
    );

  return (
    <>
      <Button variant="ghost" onClick={show}><IconShare size={14} />Share</Button>
      <dialog ref={dialog} className="m-auto w-[min(34rem,94vw)] rounded-2xl bg-white p-0"
        onClose={() => setOpen(false)} onClick={(e) => e.target === dialog.current && dialog.current?.close()}>
        <div className="space-y-5 p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-semibold tracking-tight">Share this site</h2>
            <button aria-label="Close" className="grid h-7 w-7 place-items-center rounded-md text-ink-500 hover:bg-ink-100 hover:text-ink-900" onClick={() => dialog.current?.close()}><IconClose size={15} /></button>
          </div>

          <section>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-500">People with access</h3>
            <ul className="divide-y divide-ink-100 rounded-md border border-ink-200">
              {members.data?.members.map((p) => (
                <li key={p.user_id} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
                  <span className="min-w-0 truncate">{p.name || p.email}<span className="ml-2 text-ink-400">{p.name ? p.email : ""}</span></span>
                  {p.role === "owner" ? (
                    <span className="text-xs text-ink-500">Owner</span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <select aria-label={`Role of ${p.email}`} value={p.role} className="rounded border border-ink-300 bg-white px-1.5 py-1 text-xs"
                        onChange={(e) => m.setRole.mutate({ userId: p.user_id, role: e.target.value as "designer" | "editor" })}>
                        <option value="designer">Designer</option>
                        <option value="editor">Client (content only)</option>
                      </select>
                      <button className="text-xs text-ink-500 hover:text-red-600"
                        onClick={() => window.confirm(`Remove ${p.email}?`) && m.remove.mutate(p.user_id)}>Remove</button>
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </section>

          <section className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-500">Invite someone</h3>
            <div className="flex flex-wrap gap-2">
              <select aria-label="Role for the invitation" value={role} onChange={(e) => setRole(e.target.value as "designer" | "editor")}
                className="rounded-md border border-ink-300 bg-white px-2 py-1.5 text-sm">
                <option value="editor">Client (content only)</option>
                <option value="designer">Designer</option>
              </select>
              <input aria-label="Their email (optional)" value={email} onChange={(e) => setEmail(e.target.value)} type="email"
                placeholder="their email (optional)" className="min-w-0 flex-1 rounded-md border border-ink-300 px-2.5 py-1.5 text-sm" />
              <Button onClick={createInvite} disabled={m.invite.isPending}>Create invite link</Button>
            </div>
            {(m.invite.error ?? m.setRole.error ?? m.remove.error ?? m.revoke.error) && (
              <p role="alert" className="text-xs text-red-600">{(m.invite.error ?? m.setRole.error ?? m.remove.error ?? m.revoke.error)!.message}</p>
            )}
            <p className="text-xs text-ink-400">{ROLE_HELP[role]} With an email, only that account can use the link. Links work once and expire in 7 days.</p>
            {link && (
              <div className="flex items-center gap-2 rounded-md bg-emerald-50 p-2">
                <input readOnly aria-label="Invite link" value={link} onFocus={(e) => e.target.select()} className="min-w-0 flex-1 bg-transparent text-xs" />
                <Button variant="ghost" onClick={() => { void navigator.clipboard?.writeText(link); setCopied(true); }}>{copied ? "Copied" : "Copy"}</Button>
              </div>
            )}
            {!!members.data?.invitations.length && (
              <ul className="space-y-1 text-xs text-ink-500">
                {members.data.invitations.map((i) => (
                  <li key={i.id} className="flex items-center justify-between">
                    <span>Pending {i.role === "editor" ? "client" : "designer"} invite{i.email ? ` for ${i.email}` : ""}</span>
                    <button className="hover:text-red-600" onClick={() => m.revoke.mutate(i.id)}>Revoke</button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </dialog>
    </>
  );
}
