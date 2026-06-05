"use client";

import { History, Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AuditLog, listAuditLogs } from "@/lib/api";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const token = useMemo(() => {
    if (typeof window === "undefined") {
      return "";
    }

    return window.localStorage.getItem("analytics_access_token") ?? "";
  }, []);

  useEffect(() => {
    async function loadLogs() {
      if (!token) {
        return;
      }

      setIsLoading(true);
      try {
        setLogs(await listAuditLogs(token));
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load audit logs");
      } finally {
        setIsLoading(false);
      }
    }

    void loadLogs();
  }, [token]);

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b bg-white px-5 py-4">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">Audit logs</h1>
            <p className="text-sm text-muted-foreground">
              Review administrative and governance events.
            </p>
          </div>
          <Badge variant="secondary">{logs.length} events</Badge>
        </div>
      </header>

      <section className="mx-auto max-w-7xl p-5">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-4 w-4 text-primary" aria-hidden="true" />
              Recent events
            </CardTitle>
            <CardDescription>
              {isLoading ? "Loading audit trail..." : "Superuser access is required for this view."}
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {logs.map((log) => (
              <div key={log.id} className="rounded-md border p-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">{log.action}</p>
                    <p className="text-xs text-muted-foreground">
                      {log.resource_type}
                      {log.resource_id ? `:${log.resource_id}` : ""}
                    </p>
                  </div>
                  <Badge variant="outline">{new Date(log.created_at).toLocaleString()}</Badge>
                </div>
                <pre className="mt-3 overflow-auto rounded-md bg-muted p-3 text-xs text-muted-foreground">
                  {JSON.stringify(log.event_metadata, null, 2)}
                </pre>
              </div>
            ))}
            {isLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                Loading
              </div>
            ) : null}
            {logs.length === 0 && !isLoading ? (
              <div className="rounded-md border bg-muted/30 p-6 text-sm text-muted-foreground">
                No audit events found.
              </div>
            ) : null}
            {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

