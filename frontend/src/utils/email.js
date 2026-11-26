export const SCHOOL_DOMAIN = "@sungshin.ac.kr";

// "abc" 또는 "abc@sungshin.ac.kr" 둘 다 받아서 전체 메일 주소로 바꿔줌
export function toSchoolEmail(value) {
  const v = value.trim().toLowerCase(); // 백엔드도 소문자로 저장하므로 대소문자 차이로 다른 계정이 되지 않게
  return v.includes("@") ? v : `${v}${SCHOOL_DOMAIN}`;
}

export function isSchoolEmail(email) {
  return /^[^\s@]+@sungshin\.ac\.kr$/.test(email);
}
