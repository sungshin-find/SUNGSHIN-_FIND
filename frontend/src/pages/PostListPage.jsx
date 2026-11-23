import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { errorMessage } from "../api/errors";
import { listPosts } from "../api/posts";
import { useAuth } from "../auth/useAuth";
import { PostTag } from "../components/PostTag";
import "../styles/posts.css";

// 탭은 주소의 ?type= 값으로 관리 → 새로고침하거나 링크를 공유해도 같은 탭이 열림
const TABS = [
  { key: "", label: "전체" },
  { key: "LOST", label: "분실물" },
  { key: "FOUND", label: "습득물" },
  { key: "mine", label: "내 게시물", needsLogin: true },
];

const EMPTY_TEXT = {
  "": "아직 올라온 게시물이 없어요.",
  LOST: "아직 올라온 분실물이 없어요.",
  FOUND: "아직 올라온 습득물이 없어요.",
  mine: "아직 내가 쓴 게시물이 없어요.",
};

export function PostListPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = searchParams.get("type") ?? "";

  const [posts, setPosts] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | done | error
  const [error, setError] = useState("");

  // 탭이 바뀔 때마다 목록 다시 불러오기
  useEffect(() => {
    let ignore = false; // 탭을 빠르게 바꿨을 때 이전 응답이 늦게 도착해 덮어쓰는 것 방지
    const query = tab === "mine" ? { mine: true } : { type: tab || undefined };
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
  }, [tab]);

  function changeTab(key) {
    setStatus("loading");
    setSearchParams(key ? { type: key } : {});
  }

  const writeType = tab === "FOUND" ? "FOUND" : "LOST";

  return (
    <section>
      <div className="list-head">
        <div>
          <h1 className="page__title">분실물·습득물</h1>
          <p className="page__lead">교내에서 잃어버리거나 주운 물건을 올려 주세요. 비슷한 글이 있으면 알려드려요.</p>
        </div>
        <Link to={`/posts/new?type=${writeType}`} className="btn btn--primary">
          {writeType === "FOUND" ? "습득물 등록" : "분실물 등록"}
        </Link>
      </div>

      <div className="tabs" role="tablist" aria-label="게시물 종류">
        {TABS.filter((t) => !t.needsLogin || user).map((t) => (
          <button
            key={t.key}
            type="button"
            role="tab"
            aria-selected={tab === t.key}
            className="tabs__item"
            onClick={() => changeTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {status === "loading" && <p className="list-state">불러오는 중</p>}
      {status === "error" && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}
      {status === "done" && posts.length === 0 && (
        <div className="list-empty">
          <p>{EMPTY_TEXT[tab]}</p>
          <Link to={`/posts/new?type=${writeType}`} className="btn btn--outline">
            첫 글 등록하기
          </Link>
        </div>
      )}
      {status === "done" && posts.length > 0 && (
        <ul className="post-list">
          {posts.map((post) => (
            <li key={post.id}>
              <PostTag post={post} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
