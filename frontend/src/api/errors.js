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

// 상태 코드별 기본 문구 (DRF 기본 메시지는 영어라서 이 경우엔 우리 문구로 대신함)
const STATUS_MESSAGES = {
  401: "로그인이 필요해요. 다시 로그인해 주세요.",
  403: "이 작업을 할 권한이 없어요.",
  404: "찾을 수 없어요. 삭제되었거나 주소가 잘못되었을 수 있어요.",
  429: "요청이 너무 많아요. 잠시 후 다시 시도해 주세요.",
};
const hasKorean = (text) => /[가-힣]/.test(text);

// 화면 맨 위에 띄울 한 줄짜리 에러 문구
export function errorMessage(err, fallback = "요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.") {
  if (!(err instanceof ApiError)) return "서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요.";
  if (err.status >= 500) return "서버에 문제가 생겼어요. 잠시 후 다시 시도해 주세요.";
  const data = err.data;
  const message = data && typeof data === "object" ? firstMessage(data.detail ?? data.non_field_errors ?? data) : "";
  if (message && hasKorean(message)) return message; // 백엔드가 직접 쓴 한국어 문구는 그대로
  return STATUS_MESSAGES[err.status] ?? fallback;
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
