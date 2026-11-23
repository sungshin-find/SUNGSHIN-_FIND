import { useCallback, useEffect, useMemo, useState } from "react";
import * as authApi from "../api/auth";
import { tokenStore } from "../api/token";
import { AuthContext } from "./AuthContext";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // 저장된 토큰이 있으면 "내 정보"를 받아올 때까지는 로그인 여부를 모르는 상태
  const [ready, setReady] = useState(() => !tokenStore.getAccess());

  // 새로고침해도 로그인 유지: 저장된 토큰으로 내 정보 다시 받아오기
  useEffect(() => {
    if (!tokenStore.getAccess()) return;
    authApi
      .getMe()
      .then(setUser)
      .catch(() => tokenStore.clear()) // 토큰 만료 등 → 로그아웃 상태로
      .finally(() => setReady(true));
  }, []);

  const login = useCallback(async (email, password) => {
    const tokens = await authApi.login(email, password);
    tokenStore.save(tokens);
    const me = await authApi.getMe();
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, ready, login, logout }), [user, ready, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
