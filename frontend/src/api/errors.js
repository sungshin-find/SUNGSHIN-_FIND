// 백엔드가 4xx/5xx 로 응답했을 때 던지는 에러
// data 에는 DRF 가 보낸 JSON 이 그대로 들어있음 (예: { email: ["이미 존재합니다."] })
export class ApiError extends Error {
  constructor(status, data) {
    super(`HTTP ${status}`);
    this.status = status;
    this.data = data;
  }
}

function firstMessage(value) {
  if (Array.isArray(value)) return firstMessage(value[0]);
  if (value && typeof value === "object") return firstMessage(Object.values(value)[0]);
  return value ? String(value) : "";
}

// 화면 맨 위에 띄울 한 줄짜리 에러 문구
export function errorMessage(err, fallback = "요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.") {
  if (!(err instanceof ApiError)) return "서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요.";
  const data = err.data;
  if (!data) return fallback;
  if (typeof data === "string") return fallback;
  return firstMessage(data.detail ?? data.non_field_errors ?? data) || fallback;
}

// 입력칸 아래에 띄울 필드별 에러 문구 { email: "...", password: "..." }
export function fieldErrors(err) {
  if (!(err instanceof ApiError) || !err.data || typeof err.data !== "object") return {};
  const result = {};
  for (const [key, value] of Object.entries(err.data)) {
    if (key === "detail" || key === "non_field_errors") continue;
    result[key] = firstMessage(value);
  }
  return result;
}
