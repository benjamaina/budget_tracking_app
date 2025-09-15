import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, getToken, getRefreshToken, setTokens, removeTokens } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatErrorForToast } from '@/lib/error-utils';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const token = getToken();
    const refreshToken = getRefreshToken();
    
    if (token && refreshToken) {
      // TODO: Validate token with backend or decode JWT to get user info
      setUser({ id: '1', username: 'user', email: 'user@example.com' });
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      console.log('Making login request with:', { username, password });
      const response = await authAPI.login({ username, password });
      console.log('Login response:', response.data);
      
      const { access, refresh, user_id, username: responseUsername } = response.data;
      
      setTokens(access, refresh);
      setUser({ 
        id: user_id.toString(), 
        username: responseUsername, 
        email: '' // Django doesn't return email in login response
      });
      
      toast({
        title: "Welcome back!",
        description: "You've successfully signed in.",
      });
      
      // Force navigation to dashboard
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 100);
    } catch (error: any) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
      throw error;
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      const response = await authAPI.register({ username, email, password });
      const { access, refresh, user: userData } = response.data;
      
      setTokens(access, refresh);
      setUser(userData);
      
      toast({
        title: "Account created!",
        description: "Welcome to Event Budget Manager.",
      });
    } catch (error: any) {
      const { title, description } = formatErrorForToast(error);
      toast({
        title,
        description,
        variant: "destructive",
      });
      throw error;
    }
  };

  const logout = () => {
    removeTokens();
    setUser(null);
    toast({
      title: "Signed out",
      description: "You've been successfully signed out.",
    });
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};