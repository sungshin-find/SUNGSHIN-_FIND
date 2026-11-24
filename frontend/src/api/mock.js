import { ApiError } from "./errors";

// 백엔드 없이 화면을 확인하기 위한 가짜 서버 (.env 에서 VITE_USE_MOCK=true 일 때만 사용)
// 실제 백엔드 응답 모양을 흉내만 내므로, 실제 동작 확인은 꼭 백엔드와 붙여서 할 것

const MOCK_CODE = "123456";
const db = {
  users: JSON.parse(localStorage.getItem("sf_mock_users") ?? "[]"),
  verified: new Set(),
};
const saveUsers = () => localStorage.setItem("sf_mock_users", JSON.stringify(db.users));

const fail = (status, data) => {
  throw new ApiError(status, data);
};
const currentUser = (token) => db.users.find((u) => token === `mock-${u.id}`);
const publicUser = ({ id, email, nickname }) => ({ id, email, nickname });

const routes = [
  ["GET", /^\/api\/health$/, () => ({ status: "ok", mock: true })],

  ["POST", /^\/api\/users\/email\/send-code\/$/, ({ body }) => {
    if (!body.email?.endsWith("@sungshin.ac.kr")) fail(400, { email: ["성신여대 메일만 쓸 수 있어요."] });
    if (db.users.some((u) => u.email === body.email)) fail(400, { email: ["이미 가입된 메일이에요."] });
    return { detail: "인증 코드를 보냈어요." };
  }],

  ["POST", /^\/api\/users\/email\/verify-code\/$/, ({ body }) => {
    if (body.code !== MOCK_CODE) fail(400, { code: ["인증 코드가 맞지 않아요."] });
    db.verified.add(body.email);
    return { detail: "인증되었어요." };
  }],

  ["POST", /^\/api\/users\/signup\/$/, ({ body }) => {
    if (!db.verified.has(body.email)) fail(400, { email: ["이메일 인증을 먼저 해 주세요."] });
    if (db.users.some((u) => u.nickname === body.nickname)) fail(400, { nickname: ["이미 쓰는 닉네임이에요."] });
    if (body.password.length < 8) fail(400, { password: ["비밀번호는 8자 이상이어야 해요."] });
    if (body.password !== body.password_confirm) fail(400, { password_confirm: ["비밀번호가 일치하지 않습니다."] });
    const user = { id: db.users.length + 1, email: body.email, nickname: body.nickname, password: body.password };
    db.users.push(user);
    saveUsers();
    return publicUser(user);
  }],

  ["POST", /^\/api\/users\/login\/$/, ({ body }) => {
    const user = db.users.find((u) => u.email === body.email && u.password === body.password);
    if (!user) fail(401, { detail: "이메일 또는 비밀번호가 맞지 않아요." });
    return { access: `mock-${user.id}`, refresh: `mock-refresh-${user.id}` };
  }],

  ["GET", /^\/api\/users\/me\/$/, ({ token }) => {
    const user = currentUser(token);
    if (!user) fail(401, { detail: "로그인이 필요해요." });
    return publicUser(user);
  }],
];

// ───── 게시물 (#19) ─────
const CHOICES = {
  post_type: [["LOST", "분실물"], ["FOUND", "습득물"]],
  category: [["WALLET", "지갑"], ["CARD", "카드/신분증"], ["PHONE", "휴대폰"], ["EARPHONE", "이어폰"], ["LAPTOP", "노트북/태블릿"], ["BAG", "가방"], ["UMBRELLA", "우산"], ["KEY", "열쇠"], ["CLOTHING", "의류"], ["ACCESSORY", "액세서리"], ["BOOK", "책/필기구"], ["BOTTLE", "텀블러/물병"], ["ETC", "기타"]],
  color: [["BLACK", "검정"], ["WHITE", "흰색"], ["GRAY", "회색"], ["RED", "빨강"], ["ORANGE", "주황"], ["YELLOW", "노랑"], ["GREEN", "초록"], ["BLUE", "파랑"], ["NAVY", "남색"], ["PURPLE", "보라"], ["PINK", "분홍"], ["BROWN", "갈색"], ["BEIGE", "베이지"], ["SILVER", "은색"], ["GOLD", "금색"], ["ETC", "기타"]],
  location: [["SUNGSHIN", "성신관"], ["SUJEONG", "수정관"], ["NANHYANG", "난향관"], ["UNJEONG", "운정관"], ["MUSIC", "음악관"], ["FORMATIVE", "조형관"], ["ADMIN", "행정관"], ["GREEN_CAMPUS", "운정그린캠퍼스"], ["OUTDOOR", "교내 야외"], ["ETC", "기타"]],
  status: [["OPEN", "진행중"], ["RETURNED", "반환완료"]],
};
const label = (group, value) => CHOICES[group].find(([v]) => v === value)?.[1] ?? value;
const daysAgo = (n) => new Date(Date.now() - n * 86400000).toISOString();

let nextPostId = 6;
const posts = [
  { id: 1, post_type: "LOST", title: "검정 반지갑 잃어버렸어요", category: "WALLET", color: "BLACK", location: "SUJEONG", location_detail: "3층 열람실 창가 자리", event_date: daysAgo(1).slice(0, 10), description: "안에 학생증이랑 체크카드 있어요. 찾아주시면 사례할게요.", status: "OPEN", author: "수정이", created_at: daysAgo(1) },
  { id: 2, post_type: "FOUND", title: "수정관 3층에서 검정 지갑 주웠어요", category: "WALLET", color: "BLACK", location: "SUJEONG", location_detail: "3층 복도 정수기 옆", event_date: daysAgo(1).slice(0, 10), description: "과사무실에 맡겨뒀어요.", status: "OPEN", author: "난향", created_at: daysAgo(0.5) },
  { id: 3, post_type: "FOUND", title: "에어팟 프로 케이스", category: "EARPHONE", color: "WHITE", location: "SUNGSHIN", location_detail: "1층 카페 테이블", event_date: daysAgo(3).slice(0, 10), description: "", status: "OPEN", author: "운정", created_at: daysAgo(3) },
  { id: 4, post_type: "LOST", title: "남색 장우산", category: "UMBRELLA", color: "NAVY", location: "NANHYANG", location_detail: "", event_date: daysAgo(5).slice(0, 10), description: "손잡이에 노란 스티커 붙어 있어요.", status: "RETURNED", author: "수정이", created_at: daysAgo(5) },
  { id: 5, post_type: "LOST", title: "아이패드 에어 (보라색 케이스)", category: "LAPTOP", color: "PURPLE", location: "GREEN_CAMPUS", location_detail: "도서관 2층", event_date: daysAgo(2).slice(0, 10), description: "", status: "OPEN", author: "조형", created_at: daysAgo(2) },
];

const serializePost = (p, user) => ({
  ...p,
  post_type_display: label("post_type", p.post_type),
  category_display: label("category", p.category),
  color_display: label("color", p.color),
  location_display: label("location", p.location),
  status_display: label("status", p.status),
  is_mine: Boolean(user && p.author === user.nickname),
  updated_at: p.created_at,
});

// 실제 매칭 규칙(backend/posts/matching.py)을 아주 단순하게 흉내
function mockMatches(post) {
  return posts
    .filter((o) => o.post_type !== post.post_type && o.status === "OPEN" && o.category === post.category)
    .map((o) => {
      const reasons = [`같은 종류 (${label("category", o.category)}) +40`];
      if (o.color === post.color) reasons.push(`같은 색상 (${label("color", o.color)}) +25`);
      if (o.location === post.location) reasons.push(`같은 장소 (${label("location", o.location)}) +20`);
      const score = reasons.reduce((sum, r) => sum + Number(r.split("+")[1]), 0);
      return { post: o, score, reasons };
    })
    .sort((a, b) => b.score - a.score);
}

const findPost = (id) => posts.find((p) => p.id === Number(id)) ?? fail(404, { detail: "게시물을 찾을 수 없어요." });

routes.push(
  ["GET", /^\/api\/posts\/choices\/$/, () =>
    Object.fromEntries(Object.entries(CHOICES).map(([k, list]) => [k, list.map(([value, l]) => ({ value, label: l }))]))],

  ["GET", /^\/api\/posts\/$/, ({ query, user }) =>
    posts
      .filter((p) => !query.get("type") || p.post_type === query.get("type"))
      .filter((p) => query.get("mine") !== "true" || (user && p.author === user.nickname))
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .map((p) => serializePost(p, user))],

  ["POST", /^\/api\/posts\/$/, ({ body, user }) => {
    if (!user) fail(401, { detail: "로그인이 필요해요." });
    if (!body.title?.trim()) fail(400, { title: ["제목을 입력해 주세요."] });
    const post = { ...body, id: nextPostId++, status: "OPEN", author: user.nickname, created_at: new Date().toISOString() };
    posts.push(post);
    return serializePost(post, user);
  }],

  ["GET", /^\/api\/posts\/(\d+)\/$/, ({ params, user }) => serializePost(findPost(params[0]), user)],

  ["GET", /^\/api\/posts\/(\d+)\/matches\/$/, ({ params, user }) =>
    mockMatches(findPost(params[0])).map((m) => ({ ...m, post: serializePost(m.post, user) }))],

  ["DELETE", /^\/api\/posts\/(\d+)\/$/, ({ params, user }) => {
    const post = findPost(params[0]);
    if (!user || post.author !== user.nickname) fail(403, { detail: "작성자만 삭제할 수 있어요." });
    posts.splice(posts.indexOf(post), 1);
    return null;
  }],
);

export async function mockRequest(method, url, body = {}, token) {
  await new Promise((r) => setTimeout(r, 300)); // 실제 네트워크처럼 약간 기다림
  const [path, query = ""] = url.split("?");
  for (const [m, pattern, handler] of routes) {
    const match = path.match(pattern);
    if (m === method && match) {
      return structuredClone(
        handler({ body, token, params: match.slice(1), query: new URLSearchParams(query), user: currentUser(token) }),
      );
    }
  }
  fail(404, { detail: `mock 에 없는 API: ${method} ${path}` });
}
