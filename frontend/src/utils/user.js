// 화면에 보여줄 이름: 닉네임 → 없으면 메일 아이디 → 그것도 없으면 "회원"
export function displayName(user) {
  return user?.nickname || user?.email?.split("@")[0] || "회원";
}
