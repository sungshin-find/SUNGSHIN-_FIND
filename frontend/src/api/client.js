import { ApiError } from "./errors";
import { mockRequest } from "./mock";
import { tokenStore } from "./token";

// 비워두면 같은 도메인의 /api/... 로 요청 (배포 환경: Ingress가 /api → 백엔드로 라우팅)
// 다른 서버를 직접 호출하고 싶을 때만 .env 에 주소를 넣으세요. 예) http://34.64.211.204
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

/**
 * 모든 API 호출이 거쳐가는 함수
 * - JSON 으로 주고받기
 * - 로그인 상태면 Authorization 헤더에 토큰 자동 첨부
 * - 실패하면 ApiError 를 던짐 → 화면에서 try/catch 로 처리
 */
export async function request(path, { method = "GET", body, params } = {}) {
  const query = params ? `?${new URLSearchParams(params)}` : "";
  const token = tokenStore.getAccess();

  if (USE_MOCK) return mockRequest(method, path + query, body, token);

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

  if (!res.ok) throw new ApiError(res.status, data);
  return data;
}

export const getHealth = () => request("/api/health");
