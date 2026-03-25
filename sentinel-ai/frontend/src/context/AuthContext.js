import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  authApi,
  clearAuthSession,
  getStoredAuthSession,
  saveAuthSession,
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const initialSession = getStoredAuthSession();
  const [token, setToken] = useState(initialSession?.accessToken || null);
  const [user, setUser] = useState(initialSession?.user || null);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const bootstrapSession = async () => {
      if (!token) {
        if (isMounted) {
          setIsInitializing(false);
        }
        return;
      }

      try {
        const currentUser = await authApi.getCurrentUser();

        if (!isMounted) {
          return;
        }

        setUser(currentUser);
        saveAuthSession({
          access_token: token,
          token_type: initialSession?.tokenType || 'bearer',
          expires_in: initialSession?.expiresIn || 0,
          user: currentUser,
        });
      } catch (error) {
        if (!isMounted) {
          return;
        }

        clearAuthSession();
        setToken(null);
        setUser(null);
      } finally {
        if (isMounted) {
          setIsInitializing(false);
        }
      }
    };

    bootstrapSession();

    return () => {
      isMounted = false;
    };
  }, [initialSession?.expiresIn, initialSession?.tokenType, token]);

  const login = useCallback(async (username, password) => {
    const authResponse = await authApi.login({ username, password });

    saveAuthSession(authResponse);
    setToken(authResponse.access_token);
    setUser(authResponse.user);

    return authResponse.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      if (token) {
        await authApi.logout();
      }
    } catch (error) {
      // We still clear local session even if the API request fails.
    } finally {
      clearAuthSession();
      setToken(null);
      setUser(null);
    }
  }, [token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isInitializing,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
    }),
    [isInitializing, login, logout, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
