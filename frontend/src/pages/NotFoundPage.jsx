import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <section>
      <h1 className="page__title">없는 페이지예요</h1>
      <p className="page__lead">주소를 다시 확인하거나 홈으로 돌아가 주세요.</p>
      <Link to="/" className="btn btn--primary">
        홈으로
      </Link>
    </section>
  );
}
