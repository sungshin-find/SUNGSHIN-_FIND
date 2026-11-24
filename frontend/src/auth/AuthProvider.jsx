import { useCallback, useEffect, useMemo, useState } from "react";
import * as authApi from "../api/auth";
import { SESSION_EXPIRED_EVENT } from "../api/client";
import { ApiError } from "../api/errors";
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
      .catch((err) => {
        // 토큰이 만료(401)됐을 때만 지움. 서버가 잠깐 꺼진 경우엔 토큰을 남겨서 다음에 다시 시도
        if (err instanceof ApiError && err.status === 401) tokenStore.clear();
      })
      .finally(() => setReady(true));
  }, []);

  // 사용 중 토큰이 만료되면(client.js 에서 신호) 화면도 로그아웃 상태로
  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
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
