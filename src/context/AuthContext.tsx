
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { getCurrentUser, refreshToken } from "@/lib/api/auth";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  refreshUserData: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUserData = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      return true;
    } catch (error) {
      console.error("Failed to fetch user data:", error);
      setUser(null);
      return false;
    }
  };

  const refreshUserData = async () => {
    setIsLoading(true);
    await fetchUserData();
    setIsLoading(false);
  };

  const logout = async () => {
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/login";
  };

  // Initial authentication check
  useEffect(() => {
    const checkAuth = async () => {
      setIsLoading(true);
      const token = localStorage.getItem("token");
      
      if (!token) {
        setIsLoading(false);
        return;
      }
      
      try {
        // Try to refresh the token first
        await refreshToken();
        await fetchUserData();
      } catch (error) {
        console.error("Authentication failed:", error);
        localStorage.removeItem("token");
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // Set up token refresh interval
  useEffect(() => {
    if (!user) return;
    
    const refreshInterval = setInterval(async () => {
      try {
        await refreshToken();
      } catch (error) {
        console.error("Token refresh failed:", error);
        logout();
      }
    }, 25 * 60 * 1000); // Refresh token every 25 minutes
    
    return () => clearInterval(refreshInterval);
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        refreshUserData,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
