"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { VisualizationType } from "@/lib/api";

type ReportChartProps = {
  type: VisualizationType;
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
};

export function ReportChart({ type, data, xKey, yKey }: ReportChartProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (type === "table") {
    return null;
  }

  const chartData = data.map((row) => ({
    ...row,
    [yKey]: Number(row[yKey] ?? 0),
  }));

  return (
    <div className="h-72 rounded-md border bg-muted/30 p-4">
      {isMounted ? (
        <ResponsiveContainer width="100%" height="100%">
          {type === "line" ? (
            <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey={xKey} tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} width={42} />
              <Tooltip />
              <Line dataKey={yKey} stroke="hsl(var(--primary))" strokeWidth={2} type="monotone" />
            </LineChart>
          ) : (
            <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey={xKey} tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} width={42} />
              <Tooltip cursor={{ fill: "hsl(var(--muted))" }} />
              <Bar dataKey={yKey} fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </ResponsiveContainer>
      ) : null}
    </div>
  );
}
