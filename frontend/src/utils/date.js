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
