import { createContext } from "react";

// 앱 어디서든 로그인 정보(user, login, logout)를 꺼내 쓰기 위한 통로
export const AuthContext = createContext(null);
