
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UserRound, Users, ImageIcon, Activity, FileText, BellRing, Brain } from "lucide-react";

const Dashboard = () => {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Medify AI Nexus Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Patient Management</CardTitle>
            <CardDescription>Manage patient records and information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <Users className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/patients">View Patients</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Image Analysis</CardTitle>
            <CardDescription>Upload and analyze medical images</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <ImageIcon className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/images">Image Analysis</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Analytics</CardTitle>
            <CardDescription>View system analytics and statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <Activity className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/analytics">View Analytics</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Reports</CardTitle>
            <CardDescription>Generate and view medical reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <FileText className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/reports">View Reports</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Notifications</CardTitle>
            <CardDescription>System notifications and alerts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <BellRing className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/notifications">View Notifications</Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">AI Feedback</CardTitle>
            <CardDescription>Provide feedback on AI analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex justify-between items-center">
              <Brain className="h-8 w-8 text-primary" />
              <Button asChild>
                <Link to="/ai-feedback">Provide Feedback</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
