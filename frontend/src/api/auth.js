import { request } from "./client";

// ⚠️ 회원가입(#14)만 백엔드에 구현되어 있고, 나머지는 백엔드 담당과 맞춰야 하는 예상 주소
// 주소나 필드 이름이 바뀌면 이 파일만 고치면 됨

// 학교 이메일로 인증 코드 발송
export const sendEmailCode = (email) =>
  request("/api/users/email/send/", { method: "POST", body: { email } });

// 인증 코드 확인
export const verifyEmailCode = (email, code) =>
  request("/api/users/email/verify/", { method: "POST", body: { email, code } });

// 회원가입 (#14 구현됨) → { id, email, nickname, created_at }
export const signup = ({ email, nickname, password, passwordConfirm }) =>
  request("/api/users/signup/", {
    method: "POST",
    body: { email, nickname, password, password_confirm: passwordConfirm },
  });

// 로그인 → { access, refresh }  (JWT 가정)
export const login = (email, password) =>
  request("/api/users/login/", { method: "POST", body: { email, password } });

// 내 정보 → { id, email, nickname }
export const getMe = () => request("/api/users/me/");
