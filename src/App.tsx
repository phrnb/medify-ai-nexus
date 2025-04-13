
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import PrivateRoute from "@/components/auth/PrivateRoute";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import PatientManagement from "./pages/PatientManagement";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            <Route 
              path="/" 
              element={
                <PrivateRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/patients" 
              element={
                <PrivateRoute>
                  <Layout>
                    <PatientManagement />
                  </Layout>
                </PrivateRoute>
              } 
            />
            {/* Add all other pages here as they are implemented */}
            <Route 
              path="/images" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">Image Analysis</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/analytics" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">Analytics</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/reports" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">Reports</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/notifications" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">Notifications</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/knowledge-base" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">Knowledge Base</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route 
              path="/ai-feedback" 
              element={
                <PrivateRoute>
                  <Layout>
                    <div className="container mx-auto p-6">
                      <h1 className="text-3xl font-bold">AI Feedback</h1>
                      <p className="mt-4">This page is under construction.</p>
                    </div>
                  </Layout>
                </PrivateRoute>
              } 
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
