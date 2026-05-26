import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, type ReportRow } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

const STATUSES = ["new", "reviewing", "resolved"] as const;

const STATUS_VARIANT: Record<string, "warning" | "secondary" | "success" | "muted"> = {
  new: "warning",
  reviewing: "secondary",
  resolved: "success",
};

interface ReportsProps {
  refreshNonce: number;
}

export function Reports({ refreshNonce }: ReportsProps) {
  const [status, setStatus] = useState<string>("all");
  const [rows, setRows] = useState<ReportRow[] | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const list = await api.reports(status === "all" ? undefined : status);
      setRows(list);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      toast.error("Couldn't load reports", { description: message });
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    load();
  }, [load, refreshNonce]);

  async function updateStatus(id: number, next: string) {
    const previous = rows;
    setRows((current) =>
      current ? current.map((r) => (r.id === id ? { ...r, status: next } : r)) : current
    );
    try {
      await api.updateReport(id, next);
      toast.success(`Report #${id} marked as ${next}`);
    } catch (err) {
      setRows(previous);
      const message = err instanceof Error ? err.message : "Unknown error";
      toast.error("Update failed", { description: message });
    }
  }

  const summary = useMemo(() => {
    if (!rows) return null;
    const counts = STATUSES.map((s) => ({
      status: s,
      count: rows.filter((r) => r.status === s).length,
    }));
    return counts;
  }, [rows]);

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Filter:</span>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger className="h-9 w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All reports</SelectItem>
              {STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {summary && (
          <div className="flex gap-2 text-xs">
            {summary.map((s) => (
              <Badge key={s.status} variant={STATUS_VARIANT[s.status] ?? "muted"}>
                {s.status}: {s.count}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <Card>
        <CardContent className="p-0">
          {loading && !rows ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !rows || rows.length === 0 ? (
            <EmptyRow label="No reports match this filter" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">ID</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Message</TableHead>
                  <TableHead className="w-32">Status</TableHead>
                  <TableHead className="w-28">Created</TableHead>
                  <TableHead className="w-40">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      #{row.id}
                    </TableCell>
                    <TableCell className="font-medium">{row.user_id}</TableCell>
                    <TableCell>
                      <Badge variant="muted">{row.category}</Badge>
                    </TableCell>
                    <TableCell className="max-w-[420px]">
                      <p className="whitespace-pre-wrap break-words text-sm leading-snug">
                        {row.message}
                      </p>
                    </TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANT[row.status] ?? "muted"}>
                        {row.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground" title={row.created_at}>
                      {timeAgo(row.created_at)}
                    </TableCell>
                    <TableCell>
                      <Select
                        value={row.status}
                        onValueChange={(value) => updateStatus(row.id, value)}
                      >
                        <SelectTrigger className="h-8 w-[140px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {STATUSES.map((s) => (
                            <SelectItem key={s} value={s}>
                              {s}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
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

function EmptyRow({ label }: { label: string }) {
  return (
    <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
      {label}
    </div>
  );
}
