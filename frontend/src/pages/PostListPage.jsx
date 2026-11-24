import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { errorMessage } from "../api/errors";
import { getPostChoices, listPosts } from "../api/posts";
import { useAuth } from "../auth/useAuth";
import { CategoryIcon } from "../components/CategoryIcon";
import { PostCard } from "../components/PostCard";
import { daysAgoInputValue } from "../utils/date";
import "../styles/posts.css";

// 위쪽 전환 버튼 (주소의 ?type= 값으로 관리 → 새로고침·링크 공유해도 유지)
const TYPES = [
  { key: "", label: "전체" },
  { key: "LOST", label: "분실물" },
  { key: "FOUND", label: "습득물" },
  { key: "mine", label: "내 게시물", needsLogin: true },
];

const PERIODS = [
  { value: "", label: "전체 기간" },
  { value: "3", label: "최근 3일" },
  { value: "7", label: "최근 7일" },
  { value: "30", label: "최근 30일" },
];

const EMPTY_TEXT = {
  "": "아직 올라온 게시물이 없어요.",
  LOST: "아직 올라온 분실물이 없어요.",
  FOUND: "아직 올라온 습득물이 없어요.",
  mine: "아직 내가 쓴 게시물이 없어요.",
};

export function PostListPage() {
  const { user, ready } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const rawType = searchParams.get("type") ?? "";
  // 주소에 이상한 값이 오거나, 로그아웃했는데 "내 게시물"이면 전체로 보여줌
  const type = TYPES.some((t) => t.key === rawType) && !(rawType === "mine" && ready && !user) ? rawType : "";

  const [posts, setPosts] = useState([]);
  const [choices, setChoices] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | done | error
  const [error, setError] = useState("");

  // 검색 조건 (서버에 검색 API가 없어서 받아온 목록을 화면에서 걸러냄)
  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");
  const [period, setPeriod] = useState("");
  const [since, setSince] = useState(""); // period 에 맞는 시작 날짜 (YYYY-MM-DD)
  const [keywordInput, setKeywordInput] = useState("");
  const [keyword, setKeyword] = useState(""); // 검색 버튼을 눌렀을 때 적용되는 값

  useEffect(() => {
    getPostChoices()
      .then(setChoices)
      .catch(() => setChoices(null)); // 선택지를 못 받아와도 목록은 보여줌
  }, []);

  // 분실물/습득물 전환 때마다 목록 다시 불러오기
  useEffect(() => {
    let ignore = false; // 빠르게 전환했을 때 이전 응답이 늦게 도착해 덮어쓰는 것 방지
    const query = type === "mine" ? { mine: true } : { type: type || undefined };
    listPosts(query)
      .then((data) => {
        if (ignore) return;
        setPosts(data);
        setStatus("done");
      })
      .catch((err) => {
        if (ignore) return;
        setError(errorMessage(err));
        setStatus("error");
      });
    return () => {
      ignore = true;
    };
  }, [type]);

  // 목록이나 검색 조건이 바뀔 때만 다시 거르기
  const visible = useMemo(() => {
    const word = keyword.trim().toLowerCase();
    return posts.filter(
      (p) =>
        (!category || p.category === category) &&
        (!location || p.location === location) &&
        (!since || p.event_date >= since) && // 같은 형식의 날짜 문자열이라 크기 비교 가능
        (!word || `${p.title} ${p.location_detail ?? ""} ${p.description ?? ""}`.toLowerCase().includes(word)),
    );
  }, [posts, category, location, since, keyword]);

  function changePeriod(value) {
    setPeriod(value);
    setSince(value ? daysAgoInputValue(Number(value)) : "");
  }

  function changeType(key) {
    // 이미 선택된 탭을 다시 누르면 type 이 그대로라 목록을 다시 불러오지 않음
    // → 여기서 "불러오는 중"으로 바꾸면 그 상태에 멈추므로 아무것도 하지 않음
    if (key === type) return;
    setStatus("loading");
    setSearchParams(key ? { type: key } : {});
  }

  function submitSearch(e) {
    e.preventDefault();
    setKeyword(keywordInput);
  }

  const filtered = category || location || period || keyword;
  const writeType = type === "FOUND" ? "FOUND" : "LOST";

  return (
    <section>
      <div className="explore">
        <div className="type-toggle" role="tablist" aria-label="게시물 종류">
          {TYPES.filter((t) => !t.needsLogin || user).map((t) => (
            <button
              key={t.key}
              type="button"
              role="tab"
              aria-selected={type === t.key}
              className="type-toggle__item"
              onClick={() => changeType(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>

        <form className="search-pill" onSubmit={submitSearch} role="search">
          <label className="search-pill__seg">
            <span className="search-pill__label">장소</span>
            <select value={location} onChange={(e) => setLocation(e.target.value)}>
              <option value="">모든 장소</option>
              {choices?.location.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className="search-pill__seg">
            <span className="search-pill__label">날짜</span>
            <select value={period} onChange={(e) => changePeriod(e.target.value)}>
              {PERIODS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label className="search-pill__seg search-pill__seg--grow">
            <span className="search-pill__label">검색어</span>
            <input
              type="search"
              placeholder="물건 이름, 특징"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
            />
          </label>
          <button className="search-pill__btn" aria-label="검색">
            <Search size={18} strokeWidth={2.4} aria-hidden />
          </button>
        </form>
      </div>

      {choices && (
        <div className="category-bar" role="group" aria-label="물건 종류">
          {[{ value: "", label: "전체" }, ...choices.category].map((c) => (
            <button
              key={c.value}
              type="button"
              className="category-bar__item"
              aria-pressed={category === c.value}
              onClick={() => setCategory(c.value)}
            >
              <CategoryIcon category={c.value || "ALL"} size={24} />
              {c.label}
            </button>
          ))}
        </div>
      )}

      {status === "loading" && <p className="list-state">불러오는 중</p>}
      {status === "error" && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      {status === "done" && (
        <>
          <div className="results-head">
            <p>
              게시물 <strong>{visible.length}</strong>개
            </p>
            {filtered && (
              <button
                type="button"
                className="btn btn--text"
                onClick={() => {
                  setCategory("");
                  setLocation("");
                  changePeriod("");
                  setKeywordInput("");
                  setKeyword("");
                }}
              >
                조건 지우기
              </button>
            )}
          </div>

          {visible.length === 0 ? (
            <div className="list-empty">
              <p className="list-empty__title">{filtered ? "조건에 맞는 게시물이 없어요." : EMPTY_TEXT[type]}</p>
              <p>{filtered ? "검색 조건을 바꾸거나 지워 보세요." : "잃어버리거나 주운 물건을 먼저 올려 보세요."}</p>
              <Link to={`/posts/new?type=${writeType}`} className="btn btn--outline btn--sm">
                {writeType === "FOUND" ? "습득물 등록하기" : "분실물 등록하기"}
              </Link>
            </div>
          ) : (
            <ul className="card-grid">
              {visible.map((post) => (
                <li key={post.id}>
                  <PostCard post={post} />
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}
