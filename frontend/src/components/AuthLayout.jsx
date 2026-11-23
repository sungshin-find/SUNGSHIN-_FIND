import { Link, Navigate, Outlet } from "react-router";
import { useAuth } from "../auth/useAuth";
import "../styles/auth.css";

// 로그인 / 회원가입 화면의 공통 틀
// 왼쪽: 분실물 보관표(꼬리표) 모양 소개 패널, 오른쪽: 입력 폼
export function AuthLayout() {
  const { user, ready } = useAuth();
  if (ready && user) return <Navigate to="/" replace />;

  return (
    <div className="auth">
      <aside className="auth__panel">
        <Link to="/" className="wordmark wordmark--light">
          성신 파인드
        </Link>
        <div className="claim-tag" aria-hidden="true">
          <span className="claim-tag__hole" />
          <p className="claim-tag__kind">분실물 보관표</p>
          <p className="claim-tag__title">
            잃어버린 물건,
            <br />
            학교 안에서 찾아요
          </p>
          <dl className="claim-tag__rows">
            <div>
              <dt>대상</dt>
              <dd>성신여대 학생</dd>
            </div>
            <div>
              <dt>알림</dt>
              <dd>비슷한 물건이 올라오면</dd>
            </div>
          </dl>
        </div>
        <p className="auth__panel-note">학교 메일 인증을 마친 학생만 글을 올릴 수 있어요.</p>
      </aside>
      <main className="auth__main">
        <div className="auth__form-wrap">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
