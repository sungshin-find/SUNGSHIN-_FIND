import { createElement } from "react";
import { iconFor } from "./icons";

// <CategoryIcon category="WALLET" size={20} /> → 지갑 아이콘
export function CategoryIcon({ category, size = 20, strokeWidth = 1.6, ...props }) {
  return createElement(iconFor(category), { size, strokeWidth, "aria-hidden": true, ...props });
}
