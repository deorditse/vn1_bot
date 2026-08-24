import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';
import { useDispatch } from 'react-redux';

import { useLazyGetMeQuery, useLoginMutation, useLogoutMutation } from '../api/authApi';
import type { UserProfile } from '../api/types';
import { AUTH_REQUIRED_EVENT, baseApiSlice } from '@shared/api';

type AuthContextValue = {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const devUser: UserProfile = {
  sub: 'dev-user',
  username: 'dev',
  email: 'dev@local.test',
  roles: ['dev'],
};

const isDevAuthDisabled = import.meta.env.DEV;
const DEV_LOGGED_OUT_STORAGE_KEY = 'vn1:dev-auth-logged-out';

function getDevUser(): UserProfile | null {
  return window.sessionStorage.getItem(DEV_LOGGED_OUT_STORAGE_KEY) ? null : devUser;
}

export function AuthProvider({ children }: PropsWithChildren) {
  const dispatch = useDispatch();
  const [user, setUser] = useState<UserProfile | null>(isDevAuthDisabled ? getDevUser : null);
  const [isLoading, setIsLoading] = useState(!isDevAuthDisabled);
  const [getMe] = useLazyGetMeQuery();
  const [login] = useLoginMutation();
  const [logout] = useLogoutMutation();

  const loadProfile = useCallback(async () => {
    if (isDevAuthDisabled) {
      setUser(getDevUser());
      setIsLoading(false);
      return;
    }

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
    if (isDevAuthDisabled) {
      return undefined;
    }

    const handleAuthRequired = () => setUser(null);

    window.addEventListener(AUTH_REQUIRED_EVENT, handleAuthRequired);
    return () => window.removeEventListener(AUTH_REQUIRED_EVENT, handleAuthRequired);
  }, []);

  const signIn = useCallback(async (username: string, password: string) => {
    if (isDevAuthDisabled) {
      window.sessionStorage.removeItem(DEV_LOGGED_OUT_STORAGE_KEY);
      setUser(devUser);
      return;
    }

    await login({ username, password }).unwrap();
    setUser(await getMe().unwrap());
  }, [getMe, login]);

  const signOut = useCallback(async () => {
    if (isDevAuthDisabled) {
      window.sessionStorage.setItem(DEV_LOGGED_OUT_STORAGE_KEY, '1');
      setUser(null);
      dispatch(baseApiSlice.util.resetApiState());
      return;
    }

    try {
      await logout().unwrap();
    } finally {
      setUser(null);
      dispatch(baseApiSlice.util.resetApiState());
    }
  }, [dispatch, logout]);

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
