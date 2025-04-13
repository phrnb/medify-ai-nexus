
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Pagination, 
  PaginationContent, 
  PaginationItem, 
  PaginationLink, 
  PaginationNext, 
  PaginationPrevious 
} from "@/components/ui/pagination";
import { Plus, Search, Edit, FileText } from "lucide-react";
import { fetchPatients } from "@/lib/api/patients";
import { Link } from "react-router-dom";

const PatientManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients', searchTerm, currentPage],
    queryFn: () => fetchPatients({ search: searchTerm, skip: (currentPage - 1) * 10, limit: 10 }),
  });

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Patient Management</h1>
        <Button asChild>
          <Link to="/patients/new">
            <Plus className="mr-2 h-4 w-4" /> Add New Patient
          </Link>
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Patient Records</CardTitle>
          <CardDescription>View and manage all patient records</CardDescription>
          <div className="flex w-full max-w-sm items-center space-x-2 mt-4">
            <Input 
              type="text" 
              placeholder="Search by name or MRN..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button type="submit" size="icon">
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <p>Loading patients...</p>
            </div>
          ) : error ? (
            <div className="flex justify-center items-center h-64">
              <p className="text-red-500">Error loading patients data.</p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>MRN</TableHead>
                    <TableHead>Date of Birth</TableHead>
                    <TableHead>Gender</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {patients?.map((patient) => (
                    <TableRow key={patient.id}>
                      <TableCell className="font-medium">
                        {patient.first_name} {patient.last_name}
                      </TableCell>
                      <TableCell>{patient.medical_record_number}</TableCell>
                      <TableCell>{new Date(patient.date_of_birth).toLocaleDateString()}</TableCell>
                      <TableCell>{patient.gender}</TableCell>
                      <TableCell>{patient.phone_number}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="icon" asChild>
                            <Link to={`/patients/${patient.id}`}>
                              <Edit className="h-4 w-4" />
                            </Link>
                          </Button>
                          <Button variant="outline" size="icon" asChild>
                            <Link to={`/patients/${patient.id}/reports`}>
                              <FileText className="h-4 w-4" />
                            </Link>
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              <Pagination className="mt-4">
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious 
                      onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                      disabled={currentPage === 1}
                    />
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationLink isActive>{currentPage}</PaginationLink>
                  </PaginationItem>
                  <PaginationItem>
                    <PaginationNext 
                      onClick={() => setCurrentPage(prev => prev + 1)}
                      disabled={patients?.length < 10}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PatientManagement;
