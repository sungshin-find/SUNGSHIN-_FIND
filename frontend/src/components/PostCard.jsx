import { Link } from "react-router";
import { formatDate } from "../utils/date";
import { CategoryIcon } from "./CategoryIcon";

// 게시물 카드 (에어비앤비 숙소 카드 모양)
// 사진이 없어서 윗부분은 물건 종류 아이콘 타일로 대신함. 분실물은 연보라, 습득물은 초록
// score/reasons 를 넘기면 매칭 후보 카드로 보여줌
export function PostCard({ post, score, reasons }) {
  const kind = post.post_type === "LOST" ? "lost" : "found";
  const returned = post.status === "RETURNED";

  return (
    <Link to={`/posts/${post.id}`} className={`card card--${kind}${returned ? " is-returned" : ""}`}>
      <div className="card__media">
        <CategoryIcon category={post.category} size={52} strokeWidth={1.3} />
        <span className="card__badge">{post.post_type_display}</span>
        {returned && <span className="card__badge card__badge--done">{post.status_display}</span>}
        {score !== undefined && <span className="card__score">{score}점</span>}
      </div>
      <div className="card__info">
        <div className="card__row">
          <h3 className="card__title">{post.title}</h3>
          <span className="card__date">{formatDate(post.event_date)}</span>
        </div>
        <p className="card__sub">
          {post.location_display}
          {post.location_detail && ` ${post.location_detail}`}
        </p>
        <p className="card__sub">
          {post.color_display} {post.category_display}
        </p>
        {reasons && (
          <ul className="card__reasons">
            {reasons.map((r) => (
              <li key={r}>{r.replace(/\s*\+\d+$/, "")}</li>
            ))}
          </ul>
        )}
      </div>
    </Link>
  );
}
