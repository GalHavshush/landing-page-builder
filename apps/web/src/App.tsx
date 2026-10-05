import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useMe } from "@/api/hooks";
import Dashboard from "@/pages/Dashboard";
import EditorPage from "@/pages/EditorPage";
import Login from "@/pages/Login";

function RequireAuth() {
  const me = useMe();
  if (me.isPending) return <div className="p-8 text-slate-500">Loading…</div>;
  if (!me.data) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RequireAuth />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects/:projectId" element={<EditorPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
