import { useContext } from "react";
import { AuthContext } from "./AuthContext";

// 사용법: const { user, login, logout } = useAuth();
export function useAuth() {
  return useContext(AuthContext);
}
