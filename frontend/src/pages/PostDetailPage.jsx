import { CalendarDays, ChevronLeft, MapPin, Palette } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { errorMessage } from "../api/errors";
import { deletePost, getPost, getPostMatches } from "../api/posts";
import { CategoryIcon } from "../components/CategoryIcon";
import { PostCard } from "../components/PostCard";
import { formatDate } from "../utils/date";
import "../styles/posts.css";

export function PostDetailPage() {
  const { id } = useParams(); // 주소 /posts/:id 의 id 값
  const navigate = useNavigate();

  const [post, setPost] = useState(null);
  const [matches, setMatches] = useState([]);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let ignore = false;
    // 게시물과 매칭 후보를 동시에 요청
    Promise.all([getPost(id), getPostMatches(id).catch(() => [])])
      .then(([postData, matchData]) => {
        if (ignore) return;
        setPost(postData);
        setMatches(matchData);
      })
      .catch((err) => {
        if (!ignore) setError(errorMessage(err, "게시물을 불러오지 못했어요."));
      });
    return () => {
      ignore = true;
    };
  }, [id]);

  async function handleDelete() {
    if (!window.confirm("이 게시물을 삭제할까요? 삭제하면 되돌릴 수 없어요.")) return;
    setDeleting(true);
    try {
      await deletePost(id);
      navigate("/", { replace: true });
    } catch (err) {
      setError(errorMessage(err, "삭제하지 못했어요."));
      setDeleting(false);
    }
  }

  if (error && !post) {
    return (
      <section>
        <p className="notice notice--error" role="alert">
          {error}
        </p>
        <Link to="/" className="btn btn--outline btn--sm">
          목록으로 돌아가기
        </Link>
      </section>
    );
  }
  if (!post) return <p className="list-state">불러오는 중</p>;

  const lost = post.post_type === "LOST";
  const kind = lost ? "lost" : "found";
  const other = lost ? "습득물" : "분실물";
  const returned = post.status === "RETURNED";

  const facts = [
    { icon: <CategoryIcon category={post.category} size={24} />, label: "물건 종류", value: post.category_display },
    { icon: <Palette size={24} strokeWidth={1.6} aria-hidden />, label: "색상", value: post.color_display },
    {
      icon: <MapPin size={24} strokeWidth={1.6} aria-hidden />,
      label: lost ? "잃어버린 곳" : "주운 곳",
      value: post.location_display,
      sub: post.location_detail,
    },
    { icon: <CalendarDays size={24} strokeWidth={1.6} aria-hidden />, label: lost ? "잃어버린 날" : "주운 날", value: formatDate(post.event_date) },
  ];

  return (
    <article className="detail">
      <Link to={`/?type=${post.post_type}`} className="back-link">
        <ChevronLeft size={18} aria-hidden />
        {post.post_type_display} 목록
      </Link>

      <h1 className="detail__title">{post.title}</h1>
      <p className="detail__subline">
        <span className={`chip chip--${kind}`}>{post.post_type_display}</span>
        <span className={`chip ${returned ? "chip--done" : "chip--open"}`}>{post.status_display}</span>
        <span>
          {post.location_display}
          {post.location_detail && ` ${post.location_detail}`}
        </span>
      </p>

      <div className={`detail__media detail__media--${kind}`}>
        <CategoryIcon category={post.category} size={96} strokeWidth={1.1} />
      </div>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      <div className="detail__layout">
        <div className="detail__main">
          <section className="detail__section">
            <h2 className="detail__heading">물건 정보</h2>
            <ul className="facts">
              {facts.map((f) => (
                <li key={f.label} className="facts__item">
                  <span className="facts__icon">{f.icon}</span>
                  <span>
                    <span className="facts__label">{f.label}</span>
                    <span className="facts__value">
                      {f.value}
                      {f.sub && <span className="facts__sub">{f.sub}</span>}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="detail__section">
            <h2 className="detail__heading">설명</h2>
            <p className="detail__desc">{post.description || "작성자가 남긴 설명이 없어요."}</p>
          </section>
        </div>

        {/* 오른쪽 요약 카드: 스크롤해도 따라옴 (에어비앤비 예약 카드 자리) */}
        <aside className="summary-card">
          <div className="summary-card__author">
            <span className="account-pill__avatar" aria-hidden>
              {post.author.slice(0, 1)}
            </span>
            <span>
              <strong>{post.author}</strong>
              <span className="summary-card__meta">{formatDate(post.created_at)}에 올렸어요</span>
            </span>
          </div>
          <p className="summary-card__match">
            비슷한 {other} <strong>{matches.length}</strong>건
          </p>
          <a href="#matches" className="btn btn--primary btn--block">
            비슷한 {other} 보기
          </a>
          {post.is_mine && (
            <button type="button" className="btn btn--danger btn--block" onClick={handleDelete} disabled={deleting}>
              {deleting ? "삭제하는 중…" : "게시물 삭제"}
            </button>
          )}
        </aside>
      </div>

      <section id="matches" className="matches">
        <h2 className="detail__heading">비슷한 {other}</h2>
        <p className="matches__lead">물건 종류·색상·장소·날짜가 가까울수록 점수가 높아요.</p>
        {matches.length === 0 ? (
          <div className="list-empty">
            <p className="list-empty__title">아직 비슷한 {other}이 없어요.</p>
            <p>새로 올라오면 알림으로 알려드려요.</p>
          </div>
        ) : (
          <ul className="card-grid">
            {matches.map((m) => (
              <li key={m.post.id}>
                <PostCard post={m.post} score={m.score} reasons={m.reasons} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </article>
  );
}
