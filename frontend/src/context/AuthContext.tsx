import React, { createContext, useContext, useState } from 'react';

export type UserRole = 'admin' | 'manager' | 'agent' | 'customer';

interface User {
  id: string;
  email: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, role: UserRole, user_id: string, email: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<User | null>(() => {
    const userId = localStorage.getItem('user_id');
    const email  = localStorage.getItem('email');
    const role   = localStorage.getItem('role') as UserRole | null;
    if (userId && email && role) return { id: userId, email, role };
    return null;
  });

  const login = (newToken: string, newRole: UserRole, user_id: string, email: string) => {
    localStorage.setItem('token',   newToken);
    localStorage.setItem('role',    newRole);
    localStorage.setItem('user_id', user_id);
    localStorage.setItem('email',   email);
    setToken(newToken);
    setUser({ id: user_id, email, role: newRole });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('email');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
