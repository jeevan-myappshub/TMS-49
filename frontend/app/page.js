"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { Form, FormField, FormItem, FormLabel, FormControl } from "@/components/ui/form";

export default function TimesheetPage() {
  const [timesheets, setTimesheets] = useState([]);
  const [employeeId, setEmployeeId] = useState("");
  const [weekStarting, setWeekStarting] = useState("");
  const [loading, setLoading] = useState(false);

  // Fetch timesheets
  useEffect(() => {
    fetch("/api/timesheets")
      .then((res) => res.json())
      .then(setTimesheets);
  }, []);

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await fetch("/api/timesheets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ employee_id: employeeId, week_starting: weekStarting }),
    });
    if (res.ok) {
      const newTs = await res.json();
      setTimesheets((prev) => [...prev, newTs]);
      setEmployeeId("");
      setWeekStarting("");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto py-10">
      <Card>
        <CardHeader>
          <CardTitle>Timesheets</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Employee ID</TableHead>
                <TableHead>Week Starting</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {timesheets.map((ts) => (
                <TableRow key={ts.id}>
                  <TableCell>{ts.id}</TableCell>
                  <TableCell>{ts.employee_id}</TableCell>
                  <TableCell>{ts.week_starting}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Create Timesheet</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <FormField>
              <FormItem>
                <FormLabel>Employee ID</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    required
                  />
                </FormControl>
              </FormItem>
            </FormField>
            <FormField>
              <FormItem>
                <FormLabel>Week Starting</FormLabel>
                <FormControl>
                  <Input
                    type="date"
                    value={weekStarting}
                    onChange={(e) => setWeekStarting(e.target.value)}
                    required
                  />
                </FormControl>
              </FormItem>
            </FormField>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Timesheet"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}