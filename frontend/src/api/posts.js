import { request } from "./client";

// 게시물 API (#17, #21 백엔드 구현 완료)
// DRF 페이지네이션이 켜지면 { results: [...] } 로 오므로 둘 다 처리
const asList = (data) => (Array.isArray(data) ? data : (data?.results ?? []));

// type: "LOST" | "FOUND" | undefined(전체), mine: true 면 내 게시물만
export async function listPosts({ type, mine } = {}) {
  const params = {};
  if (type) params.type = type;
  if (mine) params.mine = "true";
  return asList(await request("/api/posts/", { params }));
}

export const getPost = (id) => request(`/api/posts/${id}/`);

// 매칭 후보 → [{ post, score, reasons: ["같은 종류 (지갑) +40", ...] }]
export const getPostMatches = (id) => request(`/api/posts/${id}/matches/`);

export const createPost = (data) => request("/api/posts/", { method: "POST", body: data });

export const deletePost = (id) => request(`/api/posts/${id}/`, { method: "DELETE" });

// 등록 폼 드롭다운 선택지 → { post_type: [{value, label}], category: [...], color, location, status }
export const getPostChoices = () => request("/api/posts/choices/");
