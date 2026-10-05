import { useParams } from "react-router-dom";

export default function EditorPage() {
  const { projectId } = useParams();
  return <div className="p-8">Editor for project {projectId} (coming in M11)</div>;
}
