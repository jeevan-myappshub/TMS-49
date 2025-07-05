"use client";
import { useState, useEffect, useMemo } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
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
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const HARDCODED_EMAIL = "nathanrandall@example.net";
const IS_PRODUCTION = process.env.NODE_ENV === "production";
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

// Convert YYYY-MM-DD to MM/DD/YYYY
function toMMDDYYYY(dateStr) {
  if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return "";
  const [yyyy, mm, dd] = dateStr.split("-");
  return `${mm}/${dd}/${yyyy}`;
}

// Validate date string
function isValidDate(dateStr) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return false;
  const date = new Date(dateStr);
  return !isNaN(date.getTime());
}

export default function Home() {
  const [employee, setEmployee] = useState(null);
  const [managerHierarchy, setManagerHierarchy] = useState([]);
  const [dailyLogs, setDailyLogs] = useState([]);
  const [editedLogs, setEditedLogs] = useState({});
  const [weekStarting, setWeekStarting] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [loading, setLoading] = useState(false);
  const [showHierarchy, setShowHierarchy] = useState(false);

  // Memoize week dates
  const weekDates = useMemo(() => {
    if (!isValidDate(weekStarting)) return [];
    const startDate = new Date(weekStarting);
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      return {
        date: date.toISOString().split("T")[0],
        day: date.toLocaleString("en-US", { weekday: "long" }),
      };
    });
  }, [weekStarting]);

  // Fetch dashboard data
  useEffect(() => {
    if (isValidDate(weekStarting)) {
      fetchDashboard();
    } else {
      toast.error("Invalid week starting date. Please select a valid date.");
    }
    // eslint-disable-next-line
  }, [weekStarting]);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const formattedDate = toMMDDYYYY(weekStarting);
      const response = await fetch(
        `${BASE_URL}/api/employees/dashboard?email=${encodeURIComponent(
          HARDCODED_EMAIL
        )}&week_starting=${encodeURIComponent(formattedDate)}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
          cache: "no-store",
        }
      );
      if (!response.ok) {
        let errorMessage = `HTTP error ${response.status}`;
        if (response.status === 400) {
          const errorData = await response.json();
          errorMessage = errorData.error || "Bad request: Invalid email or week_starting.";
        } else if (response.status === 404) {
          errorMessage = "Employee not found or backend endpoint unavailable.";
        }
        throw new Error(errorMessage);
      }
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setEmployee(data.employee);
      setManagerHierarchy(data.manager_hierarchy || []);
      setDailyLogs(data.daily_logs || []);

      // Map logs for editing by date for reliability
      const logsMap = {};
      (data.daily_logs || []).forEach((log) => {
        const dateKey = log.log_date || log.date || "";
        logsMap[dateKey] = {
          time_in_am: log.time_in_am || "",
          time_out_am: log.time_out_am || "",
          time_in_pm: log.time_in_pm || "",
          time_out_pm: log.time_out_pm || "",
          description: log.description || "",
          total_hours: log.total_hours || "0:00",
          date: dateKey,
        };
      });
      // Ensure every week date has a log entry
      weekDates.forEach((day) => {
        const dateKey = toMMDDYYYY(day.date);
        if (!logsMap[dateKey]) {
          logsMap[dateKey] = {
            time_in_am: "",
            time_out_am: "",
            time_in_pm: "",
            time_out_pm: "",
            description: "",
            total_hours: "0:00",
            date: dateKey,
          };
        }
      });
      setEditedLogs(logsMap);
    } catch (error) {
      setEmployee(null);
      setManagerHierarchy([]);
      setDailyLogs([]);
      setEditedLogs({});
      toast.error(`Error fetching dashboard: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Calculate total hours
  const calculateTotalHours = (log) => {
    const parseTime = (time) => {
      if (!time) return 0;
      let [hours, minutes] = time.split(":").map(Number);
      if (isNaN(hours) || isNaN(minutes)) return 0;
      return hours * 60 + minutes;
    };

    let totalMinutes = 0;
    if (log.time_in_am && log.time_out_am) {
      const inMinutes = parseTime(log.time_in_am);
      const outMinutes = parseTime(log.time_out_am);
      if (outMinutes > inMinutes) {
        totalMinutes += outMinutes - inMinutes;
      }
    }
    if (log.time_in_pm && log.time_out_pm) {
      const inMinutes = parseTime(log.time_in_pm);
      const outMinutes = parseTime(log.time_out_pm);
      if (outMinutes > inMinutes) {
        totalMinutes += outMinutes - inMinutes;
      }
    }
    if (totalMinutes < 0) {
      return "0:00";
    }
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return `${hours}:${minutes.toString().padStart(2, "0")}`;
  };

  // Handle time input focus (set default times)
  const handleTimeInputFocus = (dateKey, field) => {
    setEditedLogs((prev) => {
      const currentLog = prev[dateKey] || {};
      if (!currentLog[field]) {
        const updatedLog = { ...currentLog };
        switch (field) {
          case "time_in_am":
            updatedLog.time_in_am = "08:00";
            break;
          case "time_out_am":
            updatedLog.time_out_am = "12:00";
            break;
          case "time_in_pm":
            updatedLog.time_in_pm = "13:00";
            break;
          case "time_out_pm":
            updatedLog.time_out_pm = "17:00";
            break;
          default:
            break;
        }
        updatedLog.total_hours = calculateTotalHours(updatedLog);
        return { ...prev, [dateKey]: updatedLog };
      }
      return prev;
    });
  };

  // Handle time input changes
  const handleTimeChange = (dateKey, field, value) => {
    setEditedLogs((prev) => {
      const updatedLog = { ...prev[dateKey], [field]: value };
      updatedLog.total_hours = calculateTotalHours(updatedLog);
      return { ...prev, [dateKey]: updatedLog };
    });
  };

  // Handle description changes
  const handleDescriptionChange = (dateKey, value) => {
    setEditedLogs((prev) => ({
      ...prev,
      [dateKey]: { ...prev[dateKey], description: value },
    }));
  };

  // Save logs
  const handleSave = async () => {
    if (!employee) {
      toast.error("No employee data available to save logs.");
      return;
    }
    setLoading(true);
    try {
      const updatedLogs = weekDates.map((day) => {
        const dateKey = toMMDDYYYY(day.date);
        const editedLog = editedLogs[dateKey] || {};
        return {
          id: editedLog.id || undefined,
          employee_id: employee.id,
          week_starting: toMMDDYYYY(weekStarting),
          date: dateKey,
          time_in_am: editedLog.time_in_am || "",
          time_out_am: editedLog.time_out_am || "",
          time_in_pm: editedLog.time_in_pm || "",
          time_out_pm: editedLog.time_out_pm || "",
          description: editedLog.description || "",
          total_hours: editedLog.total_hours || "0:00",
        };
      });
      const response = await fetch(`${BASE_URL}/api/daily-logs/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedLogs),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error ${response.status}`);
      }
      toast.success("Changes saved successfully!");
      await fetchDashboard();
    } catch (error) {
      toast.error(`Error saving logs: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Tree-like hierarchy component
  const HierarchyTree = ({ hierarchy, currentEmail }) => {
    const [expanded, setExpanded] = useState({});

    const toggleExpand = (id) => {
      setExpanded((prev) => ({
        ...prev,
        [id]: !prev[id],
      }));
    };

    const renderTree = (nodes, level = 0) => {
      return (
        <ul className={`ml-${level * 4}`}>
          {nodes.map((node) => (
            <li key={node.id} className="my-2">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleExpand(node.id)}
                  className="text-gray-500"
                >
                  {node.subordinates?.length > 0 ? (expanded[node.id] ? "▼" : "▶") : "•"}
                </button>
                <span
                  className={`${
                    node.email === currentEmail
                      ? "font-bold bg-yellow-100 px-2 py-1 rounded"
                      : ""
                  }`}
                >
                  {node.employee_name} ({node.email})
                </span>
              </div>
              {expanded[node.id] && node.subordinates && (
                <div className="border-l-2 border-gray-300 ml-6">
                  {renderTree(node.subordinates, level + 1)}
                </div>
              )}
            </li>
          ))}
        </ul>
      );
    };

    return renderTree(hierarchy);
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="w-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 bg-blue-100">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-200 p-2 rounded-full">
              <svg
                className="w-6 h-6 text-blue-800"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
            </div>
            <CardTitle className="text-2xl font-bold">Time Doctor</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {/* Employee Info Section */}
          <h2 className="text-xl font-bold mb-4">Employee Info</h2>
          {employee ? (
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <Label htmlFor="employee-name">Name</Label>
                <Input
                  id="employee-name"
                  value={employee.employee_name || ""}
                  readOnly
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="employee-email">Email</Label>
                <Input
                  id="employee-email"
                  value={employee.email || ""}
                  readOnly
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="reports-to">Reports To (ID)</Label>
                <Input
                  id="reports-to"
                  value={employee.reports_to || "No manager"}
                  readOnly
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-lg font-semibold">Manager Hierarchy</Label>
                <Dialog open={showHierarchy} onOpenChange={setShowHierarchy}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="mt-2">
                      Show Hierarchy
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Manager Hierarchy</DialogTitle>
                    </DialogHeader>
                    {managerHierarchy.length > 0 ? (
                      <HierarchyTree
                        hierarchy={managerHierarchy}
                        currentEmail={HARDCODED_EMAIL}
                      />
                    ) : (
                      <div className="text-gray-500">No manager hierarchy available.</div>
                    )}
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          ) : (
            <div>Employee not found.</div>
          )}

          {/* Timesheet and Logs Section */}
          <h2 className="text-xl font-bold mt-8 mb-4">Timesheet and Logs</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <Label htmlFor="manager-name">Manager Name</Label>
              <Input
                id="manager-name"
                value={
                  managerHierarchy.length > 0
                    ? managerHierarchy[0].employee_name
                    : "No manager"
                }
                readOnly
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="week-starting">Week Starting</Label>
              <Input
                id="week-starting"
                type="date"
                value={weekStarting}
                onChange={(e) => setWeekStarting(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          {/* Timesheet Table */}
          {loading ? (
            <div>Loading...</div>
          ) : weekDates.length === 0 ? (
            <div>Invalid week starting date. Please select a valid date.</div>
          ) : (
            <div className="w-full overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-100">
                    <TableHead className="border">Date</TableHead>
                    <TableHead className="border">Day</TableHead>
                    <TableHead className="border">Morning In (AM)</TableHead>
                    <TableHead className="border">Morning Out (AM)</TableHead>
                    <TableHead className="border">Afternoon In (PM)</TableHead>
                    <TableHead className="border">Afternoon Out (PM)</TableHead>
                    <TableHead className="border">Description</TableHead>
                    <TableHead className="border">Total Hours</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {weekDates.map((day) => {
                    const dateKey = toMMDDYYYY(day.date);
                    const log = editedLogs[dateKey] || {};
                    return (
                      <TableRow key={dateKey}>
                        <TableCell className="border">{dateKey}</TableCell>
                        <TableCell className="border">{day.day}</TableCell>
                        <TableCell className="border">
                          <Input
                            type="time"
                            value={log.time_in_am || ""}
                            onChange={(e) => handleTimeChange(dateKey, "time_in_am", e.target.value)}
                            onFocus={() => handleTimeInputFocus(dateKey, "time_in_am")}
                          />
                        </TableCell>
                        <TableCell className="border">
                          <Input
                            type="time"
                            value={log.time_out_am || ""}
                            onChange={(e) => handleTimeChange(dateKey, "time_out_am", e.target.value)}
                            onFocus={() => handleTimeInputFocus(dateKey, "time_out_am")}
                          />
                        </TableCell>
                        <TableCell className="border">
                          <Input
                            type="time"
                            value={log.time_in_pm || ""}
                            onChange={(e) => handleTimeChange(dateKey, "time_in_pm", e.target.value)}
                            onFocus={() => handleTimeInputFocus(dateKey, "time_in_pm")}
                          />
                        </TableCell>
                        <TableCell className="border">
                          <Input
                            type="time"
                            value={log.time_out_pm || ""}
                            onChange={(e) => handleTimeChange(dateKey, "time_out_pm", e.target.value)}
                            onFocus={() => handleTimeInputFocus(dateKey, "time_out_pm")}
                          />
                        </TableCell>
                        <TableCell className="border">
                          <Input
                            value={log.description || ""}
                            onChange={(e) => handleDescriptionChange(dateKey, e.target.value)}
                          />
                        </TableCell>
                        <TableCell className="border">{log.total_hours || "0:00"}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-end space-x-2">
          <Button variant="default" onClick={handleSave} disabled={loading}>
            {loading ? "Saving..." : "Save Changes"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}