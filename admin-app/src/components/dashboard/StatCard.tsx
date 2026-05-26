import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: number;
  hint?: string;
  icon: React.ReactNode;
  tone?: "default" | "warning" | "success";
}

function useCountUp(target: number, durationMs = 600) {
  const [value, setValue] = useState(0);
  const start = useRef<number | null>(null);
  const from = useRef<number>(0);

  useEffect(() => {
    from.current = value;
    start.current = null;
    let raf = 0;
    const step = (t: number) => {
      if (start.current === null) start.current = t;
      const elapsed = t - start.current;
      const p = Math.min(1, elapsed / durationMs);
      const eased = 1 - Math.pow(1 - p, 3);
      setValue(Math.round(from.current + (target - from.current) * eased));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return value;
}

export function StatCard({ label, value, hint, icon, tone = "default" }: StatCardProps) {
  const animated = useCountUp(value);
  return (
    <Card className="relative overflow-hidden">
      <div
        className={cn(
          "pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full blur-2xl opacity-50",
          tone === "warning" && "bg-warning/40",
          tone === "success" && "bg-success/40",
          tone === "default" && "bg-primary/30"
        )}
        aria-hidden
      />
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <div
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-md",
            tone === "warning" && "bg-warning/15 text-warning",
            tone === "success" && "bg-success/15 text-success",
            tone === "default" && "bg-primary/15 text-primary"
          )}
        >
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight tabular-nums">{animated}</div>
        {hint && <CardDescription className="mt-1">{hint}</CardDescription>}
      </CardContent>
    </Card>
  );
}
