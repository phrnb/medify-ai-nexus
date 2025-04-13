
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Bell, Settings, LogOut, UserRound, Sun, Moon } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/context/AuthContext";

const Navbar = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const { toast } = useToast();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle("dark");
    toast({
      title: `Theme Changed`,
      description: `Switched to ${isDarkMode ? "light" : "dark"} mode`,
      duration: 2000,
    });
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: "Logged out successfully",
        description: "You have been logged out of the system",
      });
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      toast({
        title: "Logout failed",
        description: "An error occurred during logout",
        variant: "destructive",
      });
    }
  };

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
      <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold text-primary">Medify AI Nexus</span>
            </Link>
          </div>
          
          <div className="flex items-center">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleTheme} 
              className="mr-2"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            
            <Link to="/notifications">
              <Button 
                variant="ghost" 
                size="icon" 
                className="mr-2" 
                aria-label="Notifications"
              >
                <Bell className="h-5 w-5" />
              </Button>
            </Link>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="rounded-full" 
                  aria-label="User menu"
                >
                  <UserRound className="h-5 w-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{user?.full_name || "My Account"}</DropdownMenuLabel>
                <DropdownMenuLabel className="text-xs text-gray-500">{user?.role || "User"}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <Link to="/profile" className="flex items-center w-full">
                    <UserRound className="mr-2 h-4 w-4" />
                    <span>Profile</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Link to="/settings" className="flex items-center w-full">
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <div className="flex items-center w-full">
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
