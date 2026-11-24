import { useState } from "react";
import { Link, useNavigate } from "react-router";
import * as authApi from "../api/auth";
import { errorMessage, fieldErrors } from "../api/errors";
import { TextField } from "../components/TextField";
import { SCHOOL_DOMAIN, isSchoolEmail, toSchoolEmail } from "../utils/email";

const STEPS = ["메일 인증", "코드 확인", "정보 입력"];
const STEP_TITLES = ["학교 메일을 인증해 주세요", "메일로 받은 코드를 입력해 주세요", "거의 다 됐어요"];

// 회원가입은 3단계: 1) 학교 메일로 코드 받기 → 2) 코드 확인 → 3) 닉네임·비밀번호 입력
export function SignupPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [emailId, setEmailId] = useState("");
  const [code, setCode] = useState("");
  const [form, setForm] = useState({ nickname: "", password: "", passwordConfirm: "" });

  const [errors, setErrors] = useState({}); // 입력칸별 에러
  const [notice, setNotice] = useState(""); // 상단 에러
  const [info, setInfo] = useState(""); // 상단 안내
  const [submitting, setSubmitting] = useState(false);

  const email = toSchoolEmail(emailId);

  // 세 단계 모두 "에러 초기화 → 요청 → 실패하면 에러 표시" 흐름이 같아서 하나로 묶음
  async function run(action) {
    setErrors({});
    setNotice("");
    setInfo("");
    setSubmitting(true);
    try {
      await action();
    } catch (err) {
      const byField = fieldErrors(err);
      setErrors(byField);
      if (Object.keys(byField).length === 0) setNotice(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  function sendCode(e) {
    e?.preventDefault();
    if (!isSchoolEmail(email)) {
      setErrors({ email: "성신여대 메일(@sungshin.ac.kr)만 쓸 수 있어요." });
      return;
    }
    run(async () => {
      await authApi.sendEmailCode(email);
      setCode("");
      setStep(1);
      setInfo(`${email} 로 인증 코드를 보냈어요.`);
    });
  }

  function verifyCode(e) {
    e.preventDefault();
    run(async () => {
      await authApi.verifyEmailCode(email, code.trim());
      setStep(2);
    });
  }

  function submitSignup(e) {
    e.preventDefault();
    if (form.password !== form.passwordConfirm) {
      setErrors({ password_confirm: "비밀번호가 서로 달라요." });
      return;
    }
    run(async () => {
      await authApi.signup({ email, ...form });
      navigate("/login", { state: { signedUp: true, email } });
    });
  }

  const update = (key) => (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));

  return (
    <>
      <h1 className="auth-card__head">회원가입</h1>
      <div className="auth-card__body">
        <h2 className="auth__title">{STEP_TITLES[step]}</h2>

        <ol className="steps" aria-label="가입 단계">
          {STEPS.map((label, i) => (
            <li
              key={label}
              className={i === step ? "steps__item is-current" : i < step ? "steps__item is-done" : "steps__item"}
              aria-current={i === step ? "step" : undefined}
            >
              <span className="steps__num">{i + 1}</span>
              {label}
            </li>
          ))}
        </ol>

        {info && <p className="notice notice--ok">{info}</p>}
        {notice && (
          <p className="notice notice--error" role="alert">
            {notice}
          </p>
        )}

        {step === 0 && (
          <form className="form" onSubmit={sendCode} noValidate>
            <TextField
              label="학교 메일"
              hint="이 메일로 6자리 인증 코드를 보내요."
              error={errors.email}
              value={emailId}
              onChange={(e) => setEmailId(e.target.value)}
              suffix={emailId.includes("@") ? null : SCHOOL_DOMAIN}
              autoComplete="email"
              autoFocus
            />
            <button className="btn btn--primary btn--block" disabled={submitting || !emailId.trim()}>
              {submitting ? "보내는 중…" : "인증 코드 받기"}
            </button>
          </form>
        )}

        {step === 1 && (
          <form className="form" onSubmit={verifyCode} noValidate>
            <TextField
              label="인증 코드"
              error={errors.code ?? errors.email}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              className="field__input field__input--code"
              autoFocus
            />
            <button className="btn btn--primary btn--block" disabled={submitting || code.length !== 6}>
              {submitting ? "확인하는 중…" : "코드 확인"}
            </button>
            <div className="form__row">
              <button type="button" className="btn btn--text" onClick={() => sendCode()} disabled={submitting}>
                코드 다시 받기
              </button>
              <button type="button" className="btn btn--text" onClick={() => setStep(0)} disabled={submitting}>
                메일 주소 바꾸기
              </button>
            </div>
          </form>
        )}

        {step === 2 && (
          <form className="form" onSubmit={submitSignup} noValidate>
            <p className="form__verified">
              인증된 메일 <strong>{email}</strong>
            </p>
            <TextField
              label="닉네임"
              hint="게시물 작성자로 보여요. 30자까지 쓸 수 있어요."
              error={errors.nickname}
              value={form.nickname}
              onChange={update("nickname")}
              maxLength={30}
              autoComplete="nickname"
              autoFocus
            />
            <TextField
              label="비밀번호"
              type="password"
              hint="8자 이상, 숫자로만 만들 수는 없어요."
              error={errors.password}
              value={form.password}
              onChange={update("password")}
              autoComplete="new-password"
            />
            <TextField
              label="비밀번호 확인"
              type="password"
              error={errors.password_confirm}
              value={form.passwordConfirm}
              onChange={update("passwordConfirm")}
              autoComplete="new-password"
            />
            <button
              className="btn btn--primary btn--block"
              disabled={submitting || !form.nickname.trim() || !form.password || !form.passwordConfirm}
            >
              {submitting ? "가입하는 중…" : "가입하기"}
            </button>
          </form>
        )}

        <p className="auth__switch">
          이미 계정이 있나요? <Link to="/login">로그인</Link>
        </p>
      </div>
    </>
  );
}
