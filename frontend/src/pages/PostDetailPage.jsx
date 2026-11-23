import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { errorMessage } from "../api/errors";
import { deletePost, getPost, getPostMatches } from "../api/posts";
import { PostTag } from "../components/PostTag";
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
        <Link to="/">목록으로 돌아가기</Link>
      </section>
    );
  }
  if (!post) return <p className="list-state">불러오는 중</p>;

  const kind = post.post_type === "LOST" ? "lost" : "found";
  const other = post.post_type === "LOST" ? "습득물" : "분실물";

  return (
    <article className="detail">
      <Link to={`/?type=${post.post_type}`} className="back-link">
        {post.post_type_display} 목록
      </Link>

      <header className="detail__head">
        <p className="detail__badges">
          <span className={`badge badge--${kind}`}>{post.post_type_display}</span>
          <span className={`badge ${post.status === "RETURNED" ? "badge--done" : "badge--open"}`}>
            {post.status_display}
          </span>
        </p>
        <h1 className="page__title">{post.title}</h1>
        <p className="detail__byline">
          {formatDate(post.created_at)}에 {post.author}님이 올렸어요
        </p>
      </header>

      {error && (
        <p className="notice notice--error" role="alert">
          {error}
        </p>
      )}

      <dl className="detail__facts">
        <div>
          <dt>물건 종류</dt>
          <dd>{post.category_display}</dd>
        </div>
        <div>
          <dt>색상</dt>
          <dd>{post.color_display}</dd>
        </div>
        <div>
          <dt>{post.post_type === "LOST" ? "잃어버린 곳" : "주운 곳"}</dt>
          <dd>
            {post.location_display}
            {post.location_detail && <span className="detail__sub">{post.location_detail}</span>}
          </dd>
        </div>
        <div>
          <dt>{post.post_type === "LOST" ? "잃어버린 날" : "주운 날"}</dt>
          <dd>{formatDate(post.event_date)}</dd>
        </div>
      </dl>

      {post.description && <p className="detail__desc">{post.description}</p>}

      {post.is_mine && (
        <div className="detail__actions">
          <button type="button" className="btn btn--danger btn--sm" onClick={handleDelete} disabled={deleting}>
            {deleting ? "삭제하는 중…" : "게시물 삭제"}
          </button>
        </div>
      )}

      <section className="matches" aria-labelledby="matches-title">
        <h2 id="matches-title" className="matches__title">
          비슷한 {other}
        </h2>
        <p className="matches__lead">물건 종류·색상·장소·날짜가 가까울수록 점수가 높아요.</p>
        {matches.length === 0 ? (
          <p className="list-empty list-empty--inline">
            아직 비슷한 {other}이 없어요. 새로 올라오면 알림으로 알려드려요.
          </p>
        ) : (
          <ul className="post-list">
            {matches.map((m) => (
              <li key={m.post.id}>
                <PostTag post={m.post} score={m.score} reasons={m.reasons} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </article>
  );
}
