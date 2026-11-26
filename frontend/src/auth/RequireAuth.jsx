import { Navigate, useLocation } from "react-router";
import { useAuth } from "./useAuth";

// 로그인해야 볼 수 있는 화면을 감싸는 컴포넌트
// 로그인 안 했으면 로그인 화면으로 보내고, 로그인 후 원래 화면으로 돌아오게 함
// (?type=FOUND 같은 주소 뒤 조건까지 저장해야 돌아왔을 때 그대로 유지됨)
export function RequireAuth({ children }) {
  const { user, ready } = useAuth();
  const location = useLocation();

  if (!ready) return null;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  return children;
}
