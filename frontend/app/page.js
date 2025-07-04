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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const HARDCODED_EMAIL = "nathanrandall@example.net";
const IS_PRODUCTION = process.env.NODE_ENV === "production";
const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

export default function Home() {
  const [employee, setEmployee] = useState(null);
  const [managerHierarchy, setManagerHierarchy] = useState([]);
  const [timesheets, setTimesheets] = useState([]);
  const [dailyLogs, setDailyLogs] = useState([]);
  const [editedLogs, setEditedLogs] = useState({});
  const [weekStarting, setWeekStarting] = useState(
    new Date().toISOString().split("T")[0]
  ); // YYYY-MM-DD
  const [loading, setLoading] = useState(false);
  const [showHierarchy, setShowHierarchy] = useState(false);

  // Convert YYYY-MM-DD to MM/DD/YYYY
  const toMMDDYYYY = (dateStr) => {
    if (!dateStr || !/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return "";
    const [yyyy, mm, dd] = dateStr.split("-");
    return `${mm}/${dd}/${yyyy}`;
  };

  // Validate date string
  const isValidDate = (dateStr) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return false;
    const date = new Date(dateStr);
    return !isNaN(date.getTime());
  };

  // Memoize week dates to avoid recalculation
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
      if (!isValidDate(weekStarting)) {
        throw new Error("Invalid week_starting date format. Expected YYYY-MM-DD.");
      }
      const formattedWeekStarting = toMMDDYYYY(weekStarting);
      const backendUrl = `${BASE_URL}/api/employees/dashboard?email=${encodeURIComponent(
        HARDCODED_EMAIL
      )}&week_starting=${encodeURIComponent(formattedWeekStarting)}`;
      !IS_PRODUCTION && console.log("Fetching dashboard from:", backendUrl);
      const response = await fetch(backendUrl, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
      });
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
      setTimesheets(data.timesheets || []);
      setDailyLogs(data.daily_logs || []);

      // Map logs by date for editing
      const logsMap = (data.daily_logs || []).reduce((acc, log) => {
        const timeInAM = log.time_in_am || "";
        const timeOutAM = log.time_out_am || "";
        const timeInPM = log.time_in_pm || "";
        const timeOutPM = log.time_out_pm || "";
        acc[log.id] = {
          time_in_am: timeInAM,
          time_out_am: timeOutAM,
          time_in_pm: timeInPM,
          time_out_pm: timeOutPM,
          time_in_am_meridiem: timeInAM && parseInt(timeInAM.split(":")[0]) >= 12 ? "PM" : "AM",
          time_out_am_meridiem: timeOutAM && parseInt(timeOutAM.split(":")[0]) >= 12 ? "PM" : "AM",
          time_in_pm_meridiem: timeInPM && parseInt(timeInPM.split(":")[0]) >= 12 ? "PM" : "AM",
          time_out_pm_meridiem: timeOutPM && parseInt(timeOutPM.split(":")[0]) >= 12 ? "PM" : "AM",
          description: log.description || "",
          total_hours: log.total_hours || "0:00",
          date: log.log_date || log.date || "",
        };
        return acc;
      }, {});
      // Initialize empty logs for all week dates
      weekDates.forEach((day, index) => {
        const log = data.daily_logs?.find((log) => (log.log_date || log.date) === toMMDDYYYY(day.date));
        if (!log) {
          const logId = `temp-${index}`;
          logsMap[logId] = {
            time_in_am: "",
            time_out_am: "",
            time_in_pm: "",
            time_out_pm: "",
            time_in_am_meridiem: "AM",
            time_out_am_meridiem: "AM",
            time_in_pm_meridiem: "PM",
            time_out_pm_meridiem: "PM",
            description: "",
            total_hours: "0:00",
            date: toMMDDYYYY(day.date),
          };
        }
      });
      setEditedLogs(logsMap);
      !IS_PRODUCTION && console.log("Dashboard data fetched:", logsMap);
    } catch (error) {
      setEmployee(null);
      setManagerHierarchy([]);
      setTimesheets([]);
      setDailyLogs([]);
      toast.error(`Error fetching dashboard: ${error.message}`);
      !IS_PRODUCTION && console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Convert 12-hour time with AM/PM to 24-hour time
  const to24HourTime = (time, meridiem) => {
    if (!time) return "";
    let [hours, minutes] = time.split(":").map(Number);
    if (isNaN(hours) || isNaN(minutes)) return "";
    if (meridiem === "PM" && hours < 12) hours += 12;
    if (meridiem === "AM" && hours === 12) hours = 0;
    return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
  };

  // Convert 24-hour time to 12-hour time for display
  const to12HourTime = (time) => {
    if (!time) return "";
    let [hours, minutes] = time.split(":").map(Number);
    if (isNaN(hours) || isNaN(minutes)) return "";
    const meridiem = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    return `${hours}:${minutes.toString().padStart(2, "0")}`;
  };

  // Calculate total hours with validation
  const calculateTotalHours = (timeInAM, timeOutAM, timeInPM, timeOutPM, meridiems) => {
    let totalMinutes = 0;
    const timeToMinutes = (time, meridiem) => {
      if (!time) return 0;
      let [hours, minutes] = time.split(":").map(Number);
      if (isNaN(hours) || isNaN(minutes)) return 0;
      if (meridiem === "PM" && hours < 12) hours += 12;
      if (meridiem === "AM" && hours === 12) hours = 0;
      return hours * 60 + minutes;
    };
    if (timeInAM && timeOutAM) {
      const inMinutes = timeToMinutes(timeInAM, meridiems.time_in_am_meridiem);
      const outMinutes = timeToMinutes(timeOutAM, meridiems.time_out_am_meridiem);
      if (outMinutes <= inMinutes) {
        toast.error("Morning Out time must be after In time.");
        return "0:00";
      }
      totalMinutes += outMinutes - inMinutes;
    }
    if (timeInPM && timeOutPM) {
      const inMinutes = timeToMinutes(timeInPM, meridiems.time_in_pm_meridiem);
      const outMinutes = timeToMinutes(timeOutPM, meridiems.time_out_pm_meridiem);
      if (outMinutes <= inMinutes) {
        toast.error("Afternoon Out time must be after In time.");
        return "0:00";
      }
      totalMinutes += outMinutes - inMinutes;
    }
    if (totalMinutes < 0) {
      toast.error("Total hours cannot be negative.");
      return "0:00";
    }
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return `${hours}:${minutes.toString().padStart(2, "0")}`;
  };

  // Handle time input focus (set default times)
  const handleTimeInputFocus = (id, field) => {
    setEditedLogs((prev) => {
      const currentLog = prev[id] || {};
      if (!currentLog[field]) {
        const updatedLog = { ...currentLog };
        switch (field) {
          case "time_in_am":
            updatedLog.time_in_am = "08:00";
            updatedLog.time_in_am_meridiem = "AM";
            break;
          case "time_out_am":
            updatedLog.time_out_am = "12:00";
            updatedLog.time_out_am_meridiem = "AM";
            break;
          case "time_in_pm":
            updatedLog.time_in_pm = "13:00";
            updatedLog.time_in_pm_meridiem = "PM";
            break;
          case "time_out_pm":
            updatedLog.time_out_pm = "17:00";
            updatedLog.time_out_pm_meridiem = "PM";
            break;
          default:
            break;
        }
        updatedLog.total_hours = calculateTotalHours(
          updatedLog.time_in_am,
          updatedLog.time_out_am,
          updatedLog.time_in_pm,
          updatedLog.time_out_pm,
          {
            time_in_am_meridiem: updatedLog.time_in_am_meridiem,
            time_out_am_meridiem: updatedLog.time_out_am_meridiem,
            time_in_pm_meridiem: updatedLog.time_in_pm_meridiem,
            time_out_pm_meridiem: updatedLog.time_out_pm_meridiem,
          }
        );
        return { ...prev, [id]: updatedLog };
      }
      return prev;
    });
  };

  // Handle time input changes
  const handleTimeInputChange = (id, field, value) => {
    setEditedLogs((prev) => {
      const updatedLog = { ...prev[id], [field]: value };
      updatedLog.total_hours = calculateTotalHours(
        updatedLog.time_in_am,
        updatedLog.time_out_am,
        updatedLog.time_in_pm,
        updatedLog.time_out_pm,
        {
          time_in_am_meridiem: updatedLog.time_in_am_meridiem,
          time_out_am_meridiem: updatedLog.time_out_am_meridiem,
          time_in_pm_meridiem: updatedLog.time_in_pm_meridiem,
          time_out_pm_meridiem: updatedLog.time_out_pm_meridiem,
        }
      );
      return { ...prev, [id]: updatedLog };
    });
  };

  // Handle AM/PM changes
  const handleMeridiemChange = (id, field, value) => {
    setEditedLogs((prev) => {
      const updatedLog = { ...prev[id], [field]: value };
      updatedLog.total_hours = calculateTotalHours(
        updatedLog.time_in_am,
        updatedLog.time_out_am,
        updatedLog.time_in_pm,
        updatedLog.time_out_pm,
        {
          time_in_am_meridiem: updatedLog.time_in_am_meridiem,
          time_out_am_meridiem: updatedLog.time_out_am_meridiem,
          time_in_pm_meridiem: updatedLog.time_in_pm_meridiem,
          time_out_pm_meridiem: updatedLog.time_out_pm_meridiem,
        }
      );
      return { ...prev, [id]: updatedLog };
    });
  };

  // Handle description changes
  const handleDescriptionChange = (id, value) => {
    setEditedLogs((prev) => ({
      ...prev,
      [id]: { ...prev[id], description: value },
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
      const updatedLogs = weekDates.map((day, index) => {
        const log = dailyLogs.find((log) => (log.log_date || log.date) === toMMDDYYYY(day.date)) || {};
        const logId = log.id || `temp-${index}`;
        const editedLog = editedLogs[logId] || {};
        const logData = {
          id: logId,
          employee_id: employee.id,
          week_starting: toMMDDYYYY(weekStarting),
          date: toMMDDYYYY(day.date),
          time_in_am: editedLog.time_in_am ? to24HourTime(editedLog.time_in_am, editedLog.time_in_am_meridiem) : "",
          time_out_am: editedLog.time_out_am ? to24HourTime(editedLog.time_out_am, editedLog.time_out_am_meridiem) : "",
          time_in_pm: editedLog.time_in_pm ? to24HourTime(editedLog.time_in_pm, editedLog.time_in_pm_meridiem) : "",
          time_out_pm: editedLog.time_out_pm ? to24HourTime(editedLog.time_out_pm, editedLog.time_out_pm_meridiem) : "",
          description: editedLog.description || "",
          total_hours: editedLog.total_hours || "0:00",
        };
        !IS_PRODUCTION && console.log("Saving log:", logData);
        return logData;
      });
      const response = await fetch(`${BASE_URL}/api/daily-logs/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedLogs),
      });
      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.error || `HTTP error ${response.status}`;
        if (response.status === 400) {
          throw new Error(`Bad request: ${errorData.error || "Invalid log data."}`);
        } else if (response.status === 404) {
          throw new Error("Backend endpoint /api/daily-logs/save not found.");
        }
        throw new Error(errorMessage);
      }
      toast.success("Changes saved successfully!");
      await fetchDashboard();
    } catch (error) {
      toast.error(`Error saving logs: ${error.message}`);
      !IS_PRODUCTION && console.error("Save error:", error);
    } finally {
      setLoading(false);
    }
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
            </div>
          ) : (
            <div>Employee not found.</div>
          )}

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
                    <TableHead className="border">Morning In</TableHead>
                    <TableHead className="border">Morning Out</TableHead>
                    <TableHead className="border">Afternoon In</TableHead>
                    <TableHead className="border">Afternoon Out</TableHead>
                    <TableHead className="border">Description</TableHead>
                    <TableHead className="border">Total Hours</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {weekDates.map((day, index) => {
                    const log = dailyLogs.find((log) => (log.log_date || log.date) === toMMDDYYYY(day.date)) || {};
                    const logId = log.id || `temp-${index}`;
                    return (
                      <TableRow key={logId}>
                        <TableCell className="border">{toMMDDYYYY(day.date)}</TableCell>
                        <TableCell className="border">{day.day}</TableCell>
                        <TableCell className="border">
                          <div className="flex items-center space-x-2">
                            <Input
                              type="time"
                              value={editedLogs[logId]?.time_in_am ? to12HourTime(editedLogs[logId].time_in_am) : ""}
                              onChange={(e) =>
                                handleTimeInputChange(logId, "time_in_am", e.target.value)
                              }
                              onFocus={() => handleTimeInputFocus(logId, "time_in_am")}
                            />
                            <Select
                              value={editedLogs[logId]?.time_in_am_meridiem || "AM"}
                              onValueChange={(value) =>
                                handleMeridiemChange(logId, "time_in_am_meridiem", value)
                              }
                            >
                              <SelectTrigger className="w-[80px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="AM">AM</SelectItem>
                                <SelectItem value="PM">PM</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </TableCell>
                        <TableCell className="border">
                          <div className="flex items-center space-x-2">
                            <Input
                              type="time"
                              value={editedLogs[logId]?.time_out_am ? to12HourTime(editedLogs[logId].time_out_am) : ""}
                              onChange={(e) =>
                                handleTimeInputChange(logId, "time_out_am", e.target.value)
                              }
                              onFocus={() => handleTimeInputFocus(logId, "time_out_am")}
                            />
                            <Select
                              value={editedLogs[logId]?.time_out_am_meridiem || "AM"}
                              onValueChange={(value) =>
                                handleMeridiemChange(logId, "time_out_am_meridiem", value)
                              }
                            >
                              <SelectTrigger className="w-[80px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="AM">AM</SelectItem>
                                <SelectItem value="PM">PM</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </TableCell>
                        <TableCell className="border">
                          <Input
                            value={editedLogs[logId]?.description || ""}
                            onChange={(e) => handleDescriptionChange(logId, e.target.value)}
                          />
                        </TableCell>
                        <TableCell className="border">
                          <div className="flex items-center space-x-2">
                            <Input
                              type="time"
                              value={editedLogs[logId]?.time_in_pm ? to12HourTime(editedLogs[logId].time_in_pm) : ""}
                              onChange={(e) =>
                                handleTimeInputChange(logId, "time_in_pm", e.target.value)
                              }
                              onFocus={() => handleTimeInputFocus(logId, "time_in_pm")}
                            />
                            <Select
                              value={editedLogs[logId]?.time_in_pm_meridiem || "PM"}
                              onValueChange={(value) =>
                                handleMeridiemChange(logId, "time_in_pm_meridiem", value)
                              }
                            >
                              <SelectTrigger className="w-[80px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="PM">PM</SelectItem>
                                <SelectItem value="AM">AM</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </TableCell>
                        <TableCell className="border">
                          <div className="flex items-center space-x-2">
                            <Input
                              type="time"
                              value={editedLogs[logId]?.time_out_pm ? to12HourTime(editedLogs[logId].time_out_pm) : ""}
                              onChange={(e) =>
                                handleTimeInputChange(logId, "time_out_pm", e.target.value)
                              }
                              onFocus={() => handleTimeInputFocus(logId, "time_out_pm")}
                            />
                            <Select
                              value={editedLogs[logId]?.time_out_pm_meridiem || "PM"}
                              onValueChange={(value) =>
                                handleMeridiemChange(logId, "time_out_pm_meridiem", value)
                              }
                            >
                              <SelectTrigger className="w-[80px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="PM">PM</SelectItem>
                                <SelectItem value="AM">AM</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </TableCell>
                        <TableCell className="border">
                          {editedLogs[logId]?.total_hours || "0:00"}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}

          <div className="mt-4">
            <Button
              variant="outline"
              onClick={() => setShowHierarchy(!showHierarchy)}
              className="mb-2"
            >
              {showHierarchy ? "Hide Hierarchy" : "Show Hierarchy"}
            </Button>
            {showHierarchy && (
              <div className="pl-5">
                <Label className="text-lg font-semibold">Manager Hierarchy</Label>
                {managerHierarchy.length > 0 ? (
                  <div className="mt-2">
                    {managerHierarchy.map((mgr, idx) => (
                      <div
                        key={mgr.id}
                        className={`pl-${idx * 4} flex items-center space-x-2 py-1 ${
                          idx > 0 ? "border-l-2 border-gray-300" : ""
                        }`}
                      >
                        <span className="text-gray-500">↳</span>
                        <span>
                          {idx + 1}. {mgr.employee_name} ({mgr.email})
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-2 text-gray-500">No manager</div>
                )}
              </div>
            )}
          </div>
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