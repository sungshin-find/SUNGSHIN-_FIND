import { Navigate, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";
import { Logo } from "./Logo";
import "../styles/auth.css";

// 로그인 / 회원가입 화면의 공통 틀: 가운데 카드 하나 (에어비앤비 로그인 창 모양)
export function AuthLayout() {
  const { user, ready } = useAuth();
  if (ready && user) return <Navigate to="/" replace />;

  return (
    <div className="auth">
      <header className="auth__top">
        <Logo />
      </header>
      <main className="auth__main">
        <div className="auth-card">
          <Outlet />
        </div>
        <p className="auth__note">성신여대 학교 메일 인증을 마친 학생만 이용할 수 있어요.</p>
      </main>
    </div>
  );
}
