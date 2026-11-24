import { ApiError } from "./errors";
import { tokenStore } from "./token";

// 비워두면 같은 도메인의 /api/... 로 요청 (배포 환경: Ingress가 /api → 백엔드로 라우팅)
// 다른 서버를 직접 호출하고 싶을 때만 .env 에 주소를 넣으세요. 예) http://34.64.211.204
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

/**
 * 모든 API 호출이 거쳐가는 함수
 * - JSON 으로 주고받기
 * - 로그인 상태면 Authorization 헤더에 토큰 자동 첨부 (auth: false 면 안 붙임)
 * - 실패하면 ApiError 를 던짐 → 화면에서 try/catch 로 처리
 */
export async function request(path, { method = "GET", body, params, auth = true } = {}) {
  const query = params ? `?${new URLSearchParams(params)}` : "";
  // 로그인·회원가입처럼 토큰이 필요 없는 요청에 만료된 토큰을 붙이면 401 이 나서 막힘 → 아예 안 붙임
  const token = auth ? tokenStore.getAccess() : null;

  if (USE_MOCK) {
    // mock 모드일 때만 불러옴 → 배포용 빌드에는 가짜 서버 코드가 들어가지 않음
    const { mockRequest } = await import("./mock");
    return handleAuthError(() => mockRequest(method, path + query, body, token), token);
  }

  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}${query}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text; // HTML 에러 페이지 등 JSON 이 아닌 응답
  }

  if (!res.ok) {
    if (res.status === 401 && token) expireSession();
    throw new ApiError(res.status, data);
  }
  return data;
}

// 토큰을 보냈는데 401 → 토큰 만료. 저장된 토큰을 지우고 AuthProvider 에 알림 → 화면도 로그아웃 상태로
export const SESSION_EXPIRED_EVENT = "sf:session-expired";
function expireSession() {
  tokenStore.clear();
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
}

async function handleAuthError(run, token) {
  try {
    return await run();
  } catch (err) {
    if (err instanceof ApiError && err.status === 401 && token) expireSession();
    throw err;
  }
}

export const getHealth = () => request("/api/health");
