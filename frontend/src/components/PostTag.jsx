import { Link } from "react-router";
import { formatDate } from "../utils/date";

// 게시물 목록 한 줄: 왼쪽은 보관표 꼬리(유형·날짜), 오른쪽은 내용
// 로그인 화면의 보관표와 같은 모양을 써서 서비스 전체의 통일감을 줌
export function PostTag({ post, score, reasons }) {
  const kind = post.post_type === "LOST" ? "lost" : "found";
  const returned = post.status === "RETURNED";

  return (
    <Link to={`/posts/${post.id}`} className={`post-tag post-tag--${kind}${returned ? " is-returned" : ""}`}>
      <span className="post-tag__stub">
        <span className="post-tag__hole" aria-hidden="true" />
        <span className="post-tag__kind">{post.post_type_display}</span>
        <span className="post-tag__date">{formatDate(post.event_date)}</span>
      </span>
      <span className="post-tag__body">
        <span className="post-tag__title">
          {post.title}
          {returned && <span className="badge badge--done">{post.status_display}</span>}
        </span>
        <span className="post-tag__meta">
          <span>{post.category_display}</span>
          <span>{post.color_display}</span>
          <span>
            {post.location_display}
            {post.location_detail && ` ${post.location_detail}`}
          </span>
        </span>
        {reasons && (
          <span className="post-tag__reasons">
            {reasons.map((r) => (
              <span key={r} className="reason">
                {r.replace(/\s*\+\d+$/, "")}
              </span>
            ))}
          </span>
        )}
      </span>
      {score !== undefined ? (
        <span className="post-tag__score" aria-label={`매칭 점수 ${score}점`}>
          {score}
          <small>점</small>
        </span>
      ) : (
        <span className="post-tag__author">{post.author}</span>
      )}
    </Link>
  );
}
