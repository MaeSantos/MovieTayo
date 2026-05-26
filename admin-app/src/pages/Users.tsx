import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, type UserRow } from "@/lib/api";

interface UsersProps {
  refreshNonce: number;
}

export function Users({ refreshNonce }: UsersProps) {
  const [rows, setRows] = useState<UserRow[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .users()
      .then((res) => {
        if (cancelled) return;
        setRows(res);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        toast.error("Couldn't load users", { description: err.message });
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshNonce]);

  return (
    <Card className="animate-fade-in">
      <CardContent className="p-0">
        {loading && !rows ? (
          <div className="space-y-2 p-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : !rows || rows.length === 0 ? (
          <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
            No users yet
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead className="w-24 text-right">Saved</TableHead>
                <TableHead className="w-24 text-right">Events</TableHead>
                <TableHead className="w-24 text-right">Reports</TableHead>
                <TableHead>Top genres</TableHead>
                <TableHead>Recent searches</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((u) => (
                <TableRow key={u.user_id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                        {u.user_id.slice(0, 2).toUpperCase()}
                      </div>
                      <span className="font-medium">{u.user_id}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{u.saved_count}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {u.behavior_count}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {u.report_count}
                  </TableCell>
                  <TableCell>
                    {u.top_genres.length === 0 ? (
                      <span className="text-xs text-muted-foreground">None</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {u.top_genres.slice(0, 5).map((g) => (
                          <Badge key={g.genre} variant="secondary">
                            {g.genre}
                            <span className="ml-1 text-muted-foreground">{g.count}</span>
                          </Badge>
                        ))}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    {u.recent_searches.length === 0 ? (
                      <span className="text-xs text-muted-foreground">None</span>
                    ) : (
                      <div className="flex flex-wrap gap-1">
                        {u.recent_searches.slice(0, 6).map((q) => (
                          <Badge key={q} variant="outline" className="font-normal">
                            {q}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
