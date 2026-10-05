import { Link, useNavigate, useParams } from "react-router-dom";
import { useAcceptInvite, useInvitePreview } from "@/api/hooks";
import { Button, ErrorText } from "@/components/ui";

export default function InvitePage() {
  const token = useParams().token!;
  const preview = useInvitePreview(token);
  const accept = useAcceptInvite(token);
  const navigate = useNavigate();

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-4 px-4">
      {preview.isPending && <p className="text-slate-500">Checking your invitation…</p>}
      {preview.isError && (
        <>
          <h1 className="text-xl font-semibold">This invitation can't be used</h1>
          <p className="text-sm text-slate-500">It may have expired, been used already, or been withdrawn. Ask the person who sent it for a new link.</p>
          <Link to="/" className="text-sm text-indigo-600 hover:underline">Go to your sites</Link>
        </>
      )}
      {preview.data && (
        <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h1 className="text-xl font-semibold">You're invited to “{preview.data.project_name}”</h1>
          <p className="text-sm text-slate-600">
            {preview.data.role === "editor"
              ? "You'll be able to update the text, images, prices and blog posts of this site."
              : "You'll be able to edit the design and content of this site."}
          </p>
          <ErrorText>{accept.error?.message}</ErrorText>
          <Button disabled={accept.isPending} onClick={() => accept.mutate(undefined, { onSuccess: (r) => navigate(`/projects/${r.project_id}`) })}>
            Accept and open the site
          </Button>
        </div>
      )}
    </main>
  );
}
