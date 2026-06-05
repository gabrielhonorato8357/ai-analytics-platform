import {
  Activity,
  BarChart3,
  Database,
  FileText,
  LayoutDashboard,
  Search,
  ShieldCheck,
  Users,
} from "lucide-react";
import Link from "next/link";

import { QueryVolumeChart } from "@/components/charts/query-volume-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const metrics = [
  { label: "Queries run", value: "1,284", trend: "+12.4%" },
  { label: "Saved reports", value: "46", trend: "+6" },
  { label: "Active users", value: "18", trend: "+3" },
  { label: "Audit events", value: "9,421", trend: "24h" },
];

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/" },
  { label: "Natural query", icon: Search, href: "/query" },
  { label: "Saved reports", icon: FileText, href: "/reports" },
  { label: "Users", icon: Users },
  { label: "Audit logs", icon: ShieldCheck },
];

export default function Home() {
  return (
    <main className="min-h-screen">
      <div className="grid min-h-screen lg:grid-cols-[260px_1fr]">
        <aside className="border-b bg-white lg:border-b-0 lg:border-r">
          <div className="flex h-16 items-center gap-3 border-b px-5">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <BarChart3 className="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm font-semibold">AI Analytics</p>
              <p className="text-xs text-muted-foreground">Enterprise workspace</p>
            </div>
          </div>
          <nav className="grid gap-1 p-3">
            {navigation.map((item) => (
              <Button
                key={item.label}
                asChild={Boolean(item.href)}
                variant={item.label === "Dashboard" ? "secondary" : "ghost"}
                className="justify-start gap-3"
              >
                {item.href ? (
                  <Link href={item.href}>
                    <item.icon className="h-4 w-4" aria-hidden="true" />
                    {item.label}
                  </Link>
                ) : (
                  <>
                    <item.icon className="h-4 w-4" aria-hidden="true" />
                    {item.label}
                  </>
                )}
              </Button>
            ))}
          </nav>
        </aside>

        <section className="flex min-w-0 flex-col">
          <header className="flex min-h-16 items-center justify-between gap-4 border-b bg-white px-5">
            <div>
              <h1 className="text-xl font-semibold">Analytics dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Query activity, reports, and governance at a glance.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="hidden sm:inline-flex">
                Phase 2 auth
              </Badge>
              <Button asChild variant="outline">
                <Link href="/login">Sign in</Link>
              </Button>
            </div>
          </header>

          <div className="flex-1 space-y-5 p-5">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {metrics.map((metric) => (
                <Card key={metric.label}>
                  <CardHeader className="pb-3">
                    <CardDescription>{metric.label}</CardDescription>
                    <CardTitle className="text-2xl">{metric.value}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Badge variant="secondary">{metric.trend}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
              <Card>
                <CardHeader>
                  <CardTitle>Query volume</CardTitle>
                  <CardDescription>Monthly query activity rendered with production charting.</CardDescription>
                </CardHeader>
                <CardContent>
                  <QueryVolumeChart />
                </CardContent>
              </Card>

              <div className="grid gap-5">
                <Card>
                  <CardHeader>
                    <CardTitle>Natural language query</CardTitle>
                    <CardDescription>Workflow placeholder for the AI SQL phase.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-md border bg-white p-4 text-sm text-muted-foreground">
                      Show revenue by customer segment for the last 90 days.
                    </div>
                    <Button className="w-full gap-2">
                      <Search className="h-4 w-4" aria-hidden="true" />
                      Prepare query
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Platform status</CardTitle>
                    <CardDescription>Core services expected in local development.</CardDescription>
                  </CardHeader>
                  <CardContent className="grid gap-3">
                    {[
                      { label: "API", icon: Activity },
                      { label: "PostgreSQL", icon: Database },
                      { label: "Redis", icon: Database },
                    ].map((service) => (
                      <div key={service.label} className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-sm">
                          <service.icon className="h-4 w-4 text-primary" aria-hidden="true" />
                          {service.label}
                        </div>
                        <Badge variant="secondary">configured</Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
