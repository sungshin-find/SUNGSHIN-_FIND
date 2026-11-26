import {
  Backpack,
  BookOpen,
  CreditCard,
  CupSoda,
  Gem,
  Headphones,
  KeyRound,
  LayoutGrid,
  Laptop,
  Package,
  Shirt,
  Smartphone,
  Umbrella,
  Wallet,
} from "lucide-react";

// 물건 종류(백엔드 Category 값) → 아이콘
// 백엔드에 새 종류가 추가되면 여기에 한 줄 추가 (없으면 상자 아이콘으로 표시)
export const CATEGORY_ICONS = {
  ALL: LayoutGrid,
  WALLET: Wallet,
  CARD: CreditCard,
  PHONE: Smartphone,
  EARPHONE: Headphones,
  LAPTOP: Laptop,
  BAG: Backpack,
  UMBRELLA: Umbrella,
  KEY: KeyRound,
  CLOTHING: Shirt,
  ACCESSORY: Gem,
  BOOK: BookOpen,
  BOTTLE: CupSoda,
  ETC: Package,
};

export const iconFor = (category) => CATEGORY_ICONS[category] ?? Package;
