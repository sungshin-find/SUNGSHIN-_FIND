import { Plus } from "lucide-react";
import { Link, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";
import { displayName } from "../utils/user";
import { Logo } from "./Logo";
import "../styles/layout.css";

// 로그인 후 보는 화면들의 공통 틀 (상단바 + 본문)
export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar__inner">
          <Logo />
          <nav className="topbar__account" aria-label="계정">
            <Link to="/posts/new" className="btn btn--ghost topbar__write">
              <Plus size={16} aria-hidden />
              물건 등록
            </Link>
            {user ? (
              <div className="account-pill">
                <span className="account-pill__avatar" aria-hidden>
                  {displayName(user).slice(0, 1)}
                </span>
                <span className="account-pill__name">{displayName(user)}</span>
                <button type="button" className="account-pill__logout" onClick={logout}>
                  로그아웃
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="btn btn--ghost">
                  로그인
                </Link>
                <Link to="/signup" className="btn btn--outline btn--sm topbar__signup">
                  회원가입
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}
