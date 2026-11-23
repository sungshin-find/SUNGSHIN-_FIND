export const SCHOOL_DOMAIN = "@sungshin.ac.kr";

// "abc" 또는 "abc@sungshin.ac.kr" 둘 다 받아서 전체 메일 주소로 바꿔줌
export function toSchoolEmail(value) {
  const v = value.trim();
  return v.includes("@") ? v : `${v}${SCHOOL_DOMAIN}`;
}

export function isSchoolEmail(email) {
  return /^[^\s@]+@sungshin\.ac\.kr$/.test(email);
}
