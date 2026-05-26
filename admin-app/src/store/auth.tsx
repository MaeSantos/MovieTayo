import { createContext, useCallback, useContext, useMemo, useState } from "react";
import { getAdminToken, setAdminToken } from "@/lib/api";

interface AuthContextValue {
  token: string;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string>(() => getAdminToken());

  const login = useCallback((value: string) => {
    setAdminToken(value);
    setToken(value);
  }, []);

  const logout = useCallback(() => {
    setAdminToken("");
    setToken("");
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ token, isAuthenticated: Boolean(token), login, logout }),
    [token, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
