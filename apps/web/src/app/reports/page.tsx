"use client";

import { FilePlus2, Loader2, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { ReportChart } from "@/components/charts/report-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { SavedReport, VisualizationType, createReport, deleteReport, listReports } from "@/lib/api";

const previewRows = [
  { segment: "Enterprise", revenue: 125000 },
  { segment: "Mid-market", revenue: 84000 },
  { segment: "Self-serve", revenue: 46000 },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [title, setTitle] = useState("Revenue by segment");
  const [sql, setSql] = useState("select segment, revenue from revenue_by_segment");
  const [visualizationType, setVisualizationType] = useState<VisualizationType>("bar");
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const token = useMemo(() => {
    if (typeof window === "undefined") {
      return "";
    }

    return window.localStorage.getItem("analytics_access_token") ?? "";
  }, []);

  useEffect(() => {
    async function loadReports() {
      if (!token) {
        return;
      }

      setIsLoading(true);
      try {
        setReports(await listReports(token));
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load reports");
      } finally {
        setIsLoading(false);
      }
    }

    void loadReports();
  }, [token]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      setMessage("Sign in before saving reports.");
      return;
    }

    setIsSaving(true);
    setMessage(null);

    try {
      const report = await createReport(token, {
        title,
        sql,
        visualization_type: visualizationType,
        chart_config: { xKey: "segment", yKey: "revenue" },
      });
      setReports((currentReports) => [report, ...currentReports]);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to save report");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(reportId: string) {
    if (!token) {
      return;
    }

    await deleteReport(token, reportId);
    setReports((currentReports) => currentReports.filter((report) => report.id !== reportId));
  }

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b bg-white px-5 py-4">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">Saved reports</h1>
            <p className="text-sm text-muted-foreground">
              Persist curated analytics queries and chart configuration.
            </p>
          </div>
          <Badge variant="secondary">{reports.length} saved</Badge>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-5 p-5 xl:grid-cols-[420px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FilePlus2 className="h-4 w-4 text-primary" aria-hidden="true" />
              New report
            </CardTitle>
            <CardDescription>Save validated SQL and visualization metadata.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input id="title" value={title} onChange={(event) => setTitle(event.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="visualization">Visualization</Label>
                <select
                  id="visualization"
                  className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                  value={visualizationType}
                  onChange={(event) => setVisualizationType(event.target.value as VisualizationType)}
                >
                  <option value="table">Table</option>
                  <option value="bar">Bar</option>
                  <option value="line">Line</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="sql">SQL</Label>
                <Textarea
                  id="sql"
                  className="min-h-36 font-mono"
                  value={sql}
                  onChange={(event) => setSql(event.target.value)}
                />
              </div>
              <Button className="w-full gap-2" disabled={isSaving} type="submit">
                {isSaving ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <FilePlus2 className="h-4 w-4" aria-hidden="true" />
                )}
                Save report
              </Button>
              {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
            </form>
          </CardContent>
        </Card>

        <div className="grid gap-5">
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>Chart preview uses representative result rows.</CardDescription>
            </CardHeader>
            <CardContent>
              <ReportChart data={previewRows} type={visualizationType} xKey="segment" yKey="revenue" />
              {visualizationType === "table" ? (
                <div className="rounded-md border">
                  <table className="w-full text-sm">
                    <tbody>
                      {previewRows.map((row) => (
                        <tr key={row.segment} className="border-b last:border-b-0">
                          <td className="px-3 py-2 font-medium">{row.segment}</td>
                          <td className="px-3 py-2 text-right text-muted-foreground">{row.revenue}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Report library</CardTitle>
              <CardDescription>
                {isLoading ? "Loading reports..." : "Reports are scoped to the signed-in user."}
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="flex items-center justify-between gap-4 rounded-md border p-3"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{report.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{report.sql}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{report.visualization_type}</Badge>
                    <Button
                      aria-label={`Delete ${report.title}`}
                      size="icon"
                      type="button"
                      variant="ghost"
                      onClick={() => void handleDelete(report.id)}
                    >
                      <Trash2 className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              ))}
              {reports.length === 0 ? (
                <div className="rounded-md border bg-muted/30 p-6 text-sm text-muted-foreground">
                  No reports saved yet.
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}

