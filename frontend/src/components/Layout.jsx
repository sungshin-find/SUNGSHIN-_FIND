import { Link, NavLink, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";
import "../styles/layout.css";

// 로그인 후 보는 화면들의 공통 틀 (상단바 + 본문)
export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar__inner">
          <Link to="/" className="wordmark">
            성신 파인드
          </Link>
          <nav className="topbar__nav" aria-label="주요 메뉴">
            <NavLink to="/" end>
              게시물
            </NavLink>
          </nav>
          <div className="topbar__account">
            {user ? (
              <>
                <span className="topbar__name">{user.nickname}</span>
                <button type="button" className="btn btn--quiet" onClick={logout}>
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn--quiet">
                  로그인
                </Link>
                <Link to="/signup" className="btn btn--primary btn--sm">
                  회원가입
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}
