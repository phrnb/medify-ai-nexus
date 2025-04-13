
import { useState } from "react";
import { NavLink } from "react-router-dom";
import { 
  Users, 
  ImageIcon, 
  Activity, 
  FileText, 
  BellRing, 
  Database, 
  Brain, 
  BookOpen, 
  Home,
  Menu,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const navItems = [
    { path: "/", label: "Dashboard", icon: <Home className="h-5 w-5" /> },
    { path: "/patients", label: "Patients", icon: <Users className="h-5 w-5" /> },
    { path: "/images", label: "Images", icon: <ImageIcon className="h-5 w-5" /> },
    { path: "/analytics", label: "Analytics", icon: <Activity className="h-5 w-5" /> },
    { path: "/reports", label: "Reports", icon: <FileText className="h-5 w-5" /> },
    { path: "/notifications", label: "Notifications", icon: <BellRing className="h-5 w-5" /> },
    { path: "/knowledge-base", label: "Knowledge Base", icon: <BookOpen className="h-5 w-5" /> },
    { path: "/ai-feedback", label: "AI Feedback", icon: <Brain className="h-5 w-5" /> },
  ];

  return (
    <aside 
      className={cn(
        "h-[calc(100vh-4rem)] bg-gray-100 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="h-full flex flex-col">
        <div className="p-4 flex justify-end">
          <Button variant="ghost" size="icon" onClick={toggleSidebar}>
            {collapsed ? <Menu className="h-5 w-5" /> : <X className="h-5 w-5" />}
          </Button>
        </div>
        
        <nav className="space-y-1 p-2 flex-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => cn(
                "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary text-primary-foreground" 
                  : "text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700",
                collapsed && "justify-center"
              )}
            >
              {item.icon}
              {!collapsed && <span className="ml-3">{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className={cn(
            "flex items-center", 
            collapsed ? "justify-center" : "space-x-3"
          )}>
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white font-medium">
              D
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="text-sm font-medium">Dr. Smith</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">Radiologist</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
