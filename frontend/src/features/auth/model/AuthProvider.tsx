import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';

import { useLazyGetMeQuery, useLoginMutation, useLogoutMutation } from '../api/authApi';
import type { UserProfile } from '../api/types';
import { AUTH_REQUIRED_EVENT } from '@shared/api/middleware/auth/baseQueryWithReauth';

type AuthContextValue = {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [getMe] = useLazyGetMeQuery();
  const [login] = useLoginMutation();
  const [logout] = useLogoutMutation();

  const loadProfile = useCallback(async () => {
    try {
      setUser(await getMe().unwrap());
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [getMe]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  useEffect(() => {
    const handleAuthRequired = () => setUser(null);

    window.addEventListener(AUTH_REQUIRED_EVENT, handleAuthRequired);
    return () => window.removeEventListener(AUTH_REQUIRED_EVENT, handleAuthRequired);
  }, []);

  const signIn = useCallback(async (username: string, password: string) => {
    await login({ username, password }).unwrap();
    setUser(await getMe().unwrap());
  }, [getMe, login]);

  const signOut = useCallback(async () => {
    try {
      await logout().unwrap();
    } finally {
      setUser(null);
    }
  }, [logout]);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(user),
      isLoading,
      user,
      signIn,
      signOut,
    }),
    [isLoading, signIn, signOut, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }

  return context;
}
