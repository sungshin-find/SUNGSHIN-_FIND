import { Tag } from "lucide-react";
import { Link } from "react-router";

export function Logo() {
  return (
    <Link to="/" className="logo" aria-label="성신 파인드 홈">
      <span className="logo__mark">
        <Tag size={18} strokeWidth={2.2} aria-hidden />
      </span>
      성신 파인드
    </Link>
  );
}
