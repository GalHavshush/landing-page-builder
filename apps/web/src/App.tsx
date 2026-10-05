import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { useMe } from "@/api/hooks";
import Dashboard from "@/pages/Dashboard";
import EditorPage from "@/pages/EditorPage";
import InvitePage from "@/pages/InvitePage";
import Login from "@/pages/Login";

function RequireAuth() {
  const me = useMe();
  const location = useLocation();
  if (me.isPending) return <div className="p-8 text-ink-500">Loading…</div>;
  if (!me.data) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects/:projectId" element={<EditorPage />} />
        <Route path="/invite/:token" element={<InvitePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
