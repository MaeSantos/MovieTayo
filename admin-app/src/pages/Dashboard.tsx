import { useEffect, useState } from "react";
import {
  Activity,
  Clapperboard,
  Flag,
  Heart,
  Inbox,
  Users as UsersIcon,
} from "lucide-react";
import { toast } from "sonner";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip as ChartTooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/dashboard/StatCard";
import { api, type DashboardStats } from "@/lib/api";

interface DashboardProps {
  refreshNonce: number;
  onLoadStateChange?: (loading: boolean) => void;
}

const GENRE_COLORS = [
  "hsl(217 91% 60%)",
  "hsl(142 71% 45%)",
  "hsl(38 92% 58%)",
  "hsl(280 81% 64%)",
  "hsl(0 80% 60%)",
  "hsl(199 89% 48%)",
  "hsl(166 70% 45%)",
  "hsl(330 81% 60%)",
];

export function Dashboard({ refreshNonce, onLoadStateChange }: DashboardProps) {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    onLoadStateChange?.(true);
    api
      .stats()
      .then((res) => {
        if (cancelled) return;
        setData(res);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        toast.error("Couldn't load dashboard", { description: err.message });
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
        onLoadStateChange?.(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshNonce, onLoadStateChange]);

  if (loading && !data) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const stats: Array<{
    label: string;
    value: number;
    icon: React.ReactNode;
    hint?: string;
    tone?: "default" | "warning" | "success";
  }> = [
    {
      label: "Catalog items",
      value: data.catalog_items,
      icon: <Clapperboard className="h-4 w-4" />,
      hint: "Movies, series, and anime in your library",
    },
    {
      label: "Users",
      value: data.users,
      icon: <UsersIcon className="h-4 w-4" />,
      hint: "Distinct user_ids seen across activity",
    },
    {
      label: "Saved items",
      value: data.saved_items,
      icon: <Heart className="h-4 w-4" />,
      hint: "Total items added to watchlists",
    },
    {
      label: "Open reports",
      value: data.open_reports,
      icon: <Flag className="h-4 w-4" />,
      hint: "Not yet resolved",
      tone: data.open_reports > 0 ? "warning" : "success",
    },
    {
      label: "Behavior events",
      value: data.behavior_events,
      icon: <Activity className="h-4 w-4" />,
      hint: "Logged interactions",
    },
    {
      label: "All reports",
      value: data.reports,
      icon: <Inbox className="h-4 w-4" />,
      hint: "Lifetime total",
    },
  ];

  const chartData = data.top_genres.slice(0, 8);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Top saved genres</CardTitle>
            <CardDescription>What your users are saving most</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            {chartData.length === 0 ? (
              <EmptyHint label="No saved items yet" />
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="hsl(var(--border))"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="genre"
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                      tickLine={false}
                      axisLine={false}
                      allowDecimals={false}
                    />
                    <ChartTooltip
                      cursor={{ fill: "hsl(var(--muted) / 0.4)" }}
                      contentStyle={{
                        backgroundColor: "hsl(var(--popover))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: 8,
                        fontSize: 12,
                      }}
                    />
                    <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="hsl(var(--primary))" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            {chartData.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {chartData.map((g, i) => (
                  <Badge
                    key={g.genre}
                    variant="outline"
                    style={{
                      borderColor: GENRE_COLORS[i % GENRE_COLORS.length],
                      color: GENRE_COLORS[i % GENRE_COLORS.length],
                    }}
                  >
                    {g.genre} <span className="ml-1 text-muted-foreground">·</span>
                    <span className="ml-1 text-foreground">{g.count}</span>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Top saved movies</CardTitle>
            <CardDescription>Most popular library items</CardDescription>
          </CardHeader>
          <CardContent>
            {data.top_movies.length === 0 ? (
              <EmptyHint label="No saved movies yet" />
            ) : (
              <ol className="space-y-2">
                {data.top_movies.map((m, i) => {
                  const max = data.top_movies[0]?.saved_count || 1;
                  const pct = (m.saved_count / max) * 100;
                  return (
                    <li key={m.title} className="space-y-1">
                      <div className="flex items-center justify-between gap-2 text-sm">
                        <span className="flex min-w-0 items-center gap-2">
                          <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded bg-muted text-[11px] font-semibold text-muted-foreground">
                            {i + 1}
                          </span>
                          <span className="truncate font-medium">{m.title}</span>
                        </span>
                        <span className="text-xs tabular-nums text-muted-foreground">
                          {m.saved_count}
                        </span>
                      </div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </li>
                  );
                })}
              </ol>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function EmptyHint({ label }: { label: string }) {
  return (
    <div className="flex h-32 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
      {label}
    </div>
  );
}
