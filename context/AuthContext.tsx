import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define the User type
type User = {
  id?: string;
  name: string;
  email: string;
  avatar: string;
  isLoggedIn: boolean;
};

// Define the context type
type AuthContextType = {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  updateAccessibility: (enabled: boolean) => void;
  accessibilityEnabled: boolean;
};

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  login: () => {},
  logout: () => {},
  isAuthenticated: false,
  updateAccessibility: () => {},
  accessibilityEnabled: false,
});

// Mock user for development
const mockUser: User = {
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  avatar: 'https://randomuser.me/api/portraits/lego/1.jpg',
  isLoggedIn: true,
};

// Create a provider component
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(mockUser); // For development, start with mockUser
  const [accessibilityEnabled, setAccessibilityEnabled] = useState(false);

  const login = (userData: User) => {
    setUser({ ...userData, isLoggedIn: true });
  };

  const logout = () => {
    setUser(null);
  };

  const updateAccessibility = (enabled: boolean) => {
    setAccessibilityEnabled(enabled);
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        login, 
        logout, 
        isAuthenticated: !!user, 
        updateAccessibility,
        accessibilityEnabled
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Create a custom hook to use the auth context
export const useAuth = () => useContext(AuthContext); 