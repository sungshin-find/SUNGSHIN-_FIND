import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { ApiError, errorMessage } from "../api/errors";
import { useAuth } from "../auth/useAuth";
import { TextField } from "../components/TextField";
import { SCHOOL_DOMAIN, toSchoolEmail } from "../utils/email";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  // 회원가입 직후 넘어오면 state 에 가입한 메일이 들어있음
  const justSignedUp = location.state?.signedUp;

  const [emailId, setEmailId] = useState(location.state?.email?.replace(SCHOOL_DOMAIN, "") ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault(); // form 기본 동작(페이지 새로고침) 막기
    setError("");
    setSubmitting(true);
    try {
      await login(toSchoolEmail(emailId), password);
      navigate(location.state?.from ?? "/", { replace: true });
    } catch (err) {
      // 로그인 실패(400/401)는 서버 문구가 영어일 수 있어 우리 문구로 통일
      const wrongInput = err instanceof ApiError && (err.status === 400 || err.status === 401);
      setError(wrongInput ? "이메일 또는 비밀번호가 맞지 않아요." : errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <h1 className="auth-card__head">로그인</h1>
      <div className="auth-card__body">
        <h2 className="auth__title">성신 파인드에 오신 걸 환영해요</h2>
        {justSignedUp && <p className="notice notice--ok">가입이 끝났어요. 방금 만든 계정으로 로그인해 주세요.</p>}
        {error && (
          <p className="notice notice--error" role="alert">
            {error}
          </p>
        )}

        <form className="form" onSubmit={handleSubmit} noValidate>
          <TextField
            label="학교 메일"
            value={emailId}
            onChange={(e) => setEmailId(e.target.value)}
            suffix={emailId.includes("@") ? null : SCHOOL_DOMAIN}
            autoComplete="username"
            autoFocus
            required
          />
          <TextField
            label="비밀번호"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
          <button className="btn btn--primary btn--block" disabled={submitting || !emailId || !password}>
            {submitting ? "로그인하는 중…" : "로그인"}
          </button>
        </form>

        <p className="auth__switch">
          아직 계정이 없나요? <Link to="/signup">회원가입</Link>
        </p>
      </div>
    </>
  );
}
