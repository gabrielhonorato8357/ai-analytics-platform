"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const data = [
  { month: "Jan", queries: 420 },
  { month: "Feb", queries: 580 },
  { month: "Mar", queries: 750 },
  { month: "Apr", queries: 490 },
  { month: "May", queries: 880 },
  { month: "Jun", queries: 680 },
  { month: "Jul", queries: 930 },
  { month: "Aug", queries: 780 },
  { month: "Sep", queries: 620 },
  { month: "Oct", queries: 840 },
  { month: "Nov", queries: 700 },
  { month: "Dec", queries: 960 },
];

export function QueryVolumeChart() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  return (
    <div className="h-72 rounded-md border bg-muted/30 p-4">
      {isMounted ? (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} width={42} />
            <Tooltip cursor={{ fill: "hsl(var(--muted))" }} />
            <Bar dataKey="queries" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ) : null}
    </div>
  );
}
