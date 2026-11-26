// "2026-11-20" 또는 ISO 날짜 → "11월 20일"
export function formatDate(value) {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return `${d.getMonth() + 1}월 ${d.getDate()}일`;
}

// 오늘 날짜를 <input type="date"> 형식(YYYY-MM-DD)으로
export function todayInputValue() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// n일 전 날짜를 YYYY-MM-DD 로 (기간 필터용, 이벤트 핸들러 안에서만 호출)
export function daysAgoInputValue(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  const pad = (v) => String(v).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}
