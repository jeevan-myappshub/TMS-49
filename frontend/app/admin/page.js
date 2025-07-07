"use client";
import { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

export default function AdminPage() {
  const [employees, setEmployees] = useState([]);
  const [managers, setManagers] = useState({});
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [employeeTimesheets, setEmployeeTimesheets] = useState([]);
  const [selectedTimesheet, setSelectedTimesheet] = useState(null);
  const [dailyLogs, setDailyLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showEmployeeDialog, setShowEmployeeDialog] = useState(false);
  const [showLogsDialog, setShowLogsDialog] = useState(false);

  // Add Employee Dialog State
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newEmpName, setNewEmpName] = useState("");
  const [newEmpEmail, setNewEmpEmail] = useState("");
  const [newEmpManagerId, setNewEmpManagerId] = useState("");

  // Fetch all employees and build manager map
  useEffect(() => {
    fetchAllEmployees();
    // eslint-disable-next-line
  }, []);

  const fetchAllEmployees = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/api/employees`);
      if (!res.ok) throw new Error("Failed to fetch employees");
      let data = await res.json();
      // Sort employees by id ascending
      data = data.sort((a, b) => a.id - b.id);
      setEmployees(data);
      // Build manager map: id -> name
      const mgrMap = {};
      data.forEach((emp) => {
        mgrMap[emp.id] = emp.employee_name;
      });
      setManagers(mgrMap);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch timesheets for selected employee
  const handleEmployeeSelect = async (emp) => {
    setSelectedEmployee(emp);
    setEmployeeTimesheets([]);
    setDailyLogs([]);
    setShowEmployeeDialog(true);
    setShowLogsDialog(false);
    setLoading(true);
    try {
      const res = await fetch(
        `${BASE_URL}/api/timesheets/by-employee-name?employee_name=${encodeURIComponent(
          emp.employee_name
        )}`
      );
      if (!res.ok) throw new Error("Failed to fetch employee timesheets");
      let data = await res.json();
      // Sort timesheets by id ascending
      data = data.sort((a, b) => a.id - b.id);
      setEmployeeTimesheets(data);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch daily logs for selected timesheet
  const handleTimesheetSelect = async (ts) => {
    setSelectedTimesheet(ts);
    setDailyLogs([]);
    setShowLogsDialog(true);
    setLoading(true);
    try {
      const res = await fetch(
        `${BASE_URL}/api/timesheets/${ts.id}/daily-logs`
      );
      if (!res.ok) throw new Error("Failed to fetch daily logs");
      let data = await res.json();
      // Sort daily logs by id ascending
      data = data.sort((a, b) => a.id - b.id);
      setDailyLogs(data);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to get manager name by id
  const getManagerName = (reportsToId) => {
    if (!reportsToId) return "None";
    return managers[reportsToId] || "Unknown";
  };

  // Add Employee Handler
  const handleAddEmployee = async (e) => {
    e.preventDefault();
    if (!newEmpName || !newEmpEmail) {
      toast.error("Name and Email are required.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/api/employees`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employee_name: newEmpName,
          email: newEmpEmail,
          reports_to: newEmpManagerId || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to add employee");
      }
      toast.success("Employee added successfully!");
      setShowAddDialog(false);
      setNewEmpName("");
      setNewEmpEmail("");
      setNewEmpManagerId("");
      await fetchAllEmployees();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="w-full mb-6">
        <CardHeader className="bg-blue-100 text-center py-4 flex flex-col md:flex-row md:justify-between md:items-center">
          <CardTitle className="text-2xl font-bold">Admin Dashboard</CardTitle>
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button
                variant="default"
                className="mt-4 md:mt-0"
                onClick={() => setShowAddDialog(true)}
              >
                + Add Employee
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Employee</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleAddEmployee} className="space-y-4">
                <div>
                  <Label htmlFor="emp-name">Name</Label>
                  <Input
                    id="emp-name"
                    value={newEmpName}
                    onChange={(e) => setNewEmpName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="emp-email">Email</Label>
                  <Input
                    id="emp-email"
                    type="email"
                    value={newEmpEmail}
                    onChange={(e) => setNewEmpEmail(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="emp-manager">Manager</Label>
                  <Select
                    value={newEmpManagerId}
                    onValueChange={setNewEmpManagerId}
                  >
                    <SelectTrigger id="emp-manager">
                      <SelectValue placeholder="Select Manager (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {employees.map((emp) => (
                        <SelectItem key={emp.id} value={String(emp.id)}>
                          {emp.employee_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end">
                  <Button type="submit" variant="default" disabled={loading}>
                    Add Employee
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          <h2 className="text-xl font-bold mb-4">All Employees</h2>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Manager</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {employees.map((emp) => (
                  <TableRow key={emp.id}>
                    <TableCell>{emp.id}</TableCell>
                    <TableCell>{emp.employee_name}</TableCell>
                    <TableCell>{emp.email}</TableCell>
                    <TableCell>{getManagerName(emp.reports_to)}</TableCell>
                    <TableCell>
                      <Dialog open={showEmployeeDialog && selectedEmployee?.id === emp.id} onOpenChange={setShowEmployeeDialog}>
                        <DialogTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEmployeeSelect(emp)}
                          >
                            View Timesheets
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>
                              Timesheets for {emp.employee_name}
                            </DialogTitle>
                          </DialogHeader>
                          {loading ? (
                            <div>Loading...</div>
                          ) : employeeTimesheets.length === 0 ? (
                            <div>No timesheets found for this employee.</div>
                          ) : (
                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>ID</TableHead>
                                  <TableHead>Week Starting</TableHead>
                                  <TableHead>Actions</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {employeeTimesheets.map((ts) => (
                                  <TableRow key={ts.id}>
                                    <TableCell>{ts.id}</TableCell>
                                    <TableCell>
                                      {ts.week_starting
                                        ? new Date(ts.week_starting).toLocaleDateString()
                                        : ""}
                                    </TableCell>
                                    <TableCell>
                                      <Dialog open={showLogsDialog && selectedTimesheet?.id === ts.id} onOpenChange={setShowLogsDialog}>
                                        <DialogTrigger asChild>
                                          <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleTimesheetSelect(ts)}
                                          >
                                            View Daily Logs
                                          </Button>
                                        </DialogTrigger>
                                        <DialogContent>
                                          <DialogHeader>
                                            <DialogTitle>
                                              Daily Logs for Timesheet #{ts.id} (
                                              {ts.week_starting
                                                ? new Date(ts.week_starting).toLocaleDateString()
                                                : ""}
                                              )
                                            </DialogTitle>
                                          </DialogHeader>
                                          {loading ? (
                                            <div>Loading...</div>
                                          ) : dailyLogs.length === 0 ? (
                                            <div>No daily logs found for this timesheet.</div>
                                          ) : (
                                            <Table>
                                              <TableHeader>
                                                <TableRow>
                                                  <TableHead>ID</TableHead>
                                                  <TableHead>Date</TableHead>
                                                  <TableHead>Day</TableHead>
                                                  <TableHead>Morning In</TableHead>
                                                  <TableHead>Morning Out</TableHead>
                                                  <TableHead>Afternoon In</TableHead>
                                                  <TableHead>Afternoon Out</TableHead>
                                                  <TableHead>Description</TableHead>
                                                  <TableHead>Total Hours</TableHead>
                                                </TableRow>
                                              </TableHeader>
                                              <TableBody>
                                                {dailyLogs.map((log) => (
                                                  <TableRow key={log.id}>
                                                    <TableCell>{log.id}</TableCell>
                                                    <TableCell>
                                                      {log.log_date
                                                        ? new Date(log.log_date).toLocaleDateString()
                                                        : ""}
                                                    </TableCell>
                                                    <TableCell>{log.day_of_week}</TableCell>
                                                    <TableCell>{log.morning_in?.slice(0, 5) || ""}</TableCell>
                                                    <TableCell>{log.morning_out?.slice(0, 5) || ""}</TableCell>
                                                    <TableCell>{log.afternoon_in?.slice(0, 5) || ""}</TableCell>
                                                    <TableCell>{log.afternoon_out?.slice(0, 5) || ""}</TableCell>
                                                    <TableCell>{log.description}</TableCell>
                                                    <TableCell>{log.total_hours?.slice(0, 5) || "0:00"}</TableCell>
                                                  </TableRow>
                                                ))}
                                              </TableBody>
                                            </Table>
                                          )}
                                        </DialogContent>
                                      </Dialog>
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          )}
                        </DialogContent>
                      </Dialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}