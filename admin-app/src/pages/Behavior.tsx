import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, type BehaviorRow } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

interface BehaviorProps {
  refreshNonce: number;
}

export function Behavior({ refreshNonce }: BehaviorProps) {
  const [rows, setRows] = useState<BehaviorRow[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .behavior()
      .then((res) => {
        if (cancelled) return;
        setRows(res);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        toast.error("Couldn't load behavior events", { description: err.message });
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshNonce]);

  const filtered = useMemo(() => {
    if (!rows) return rows;
    const q = query.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) =>
      [r.user_id, r.interaction_type, r.title, r.content_id]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    );
  }, [rows, query]);

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by user, type, or movie…"
            className="pl-9"
          />
        </div>
        <span className="text-xs text-muted-foreground">
          {filtered ? `${filtered.length} event${filtered.length === 1 ? "" : "s"}` : ""}
        </span>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading && !rows ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !filtered || filtered.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              No events match
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-28">When</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Movie</TableHead>
                  <TableHead className="w-20 text-right">Dwell</TableHead>
                  <TableHead>Context</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell
                      className="whitespace-nowrap text-xs text-muted-foreground"
                      title={row.created_at}
                    >
                      {timeAgo(row.created_at)}
                    </TableCell>
                    <TableCell className="font-medium">{row.user_id}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{row.interaction_type}</Badge>
                    </TableCell>
                    <TableCell>{row.title || row.content_id || "—"}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {row.dwell_time ? `${Number(row.dwell_time).toFixed(1)}s` : "—"}
                    </TableCell>
                    <TableCell>
                      <code className="block max-w-[320px] truncate rounded bg-muted px-2 py-1 font-mono text-[11px]">
                        {JSON.stringify(row.context ?? {})}
                      </code>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
