import { useEffect, useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown, Search } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { useDebounce } from "@/hooks/use-debounce";
import { api, type CatalogRow } from "@/lib/api";
import { cn } from "@/lib/utils";

type SortKey = keyof Pick<CatalogRow, "id" | "title" | "kind" | "genres">;
type SortDir = "asc" | "desc";

interface CatalogProps {
  refreshNonce: number;
}

export function Catalog({ refreshNonce }: CatalogProps) {
  const [query, setQuery] = useState("");
  const debounced = useDebounce(query, 300);
  const [rows, setRows] = useState<CatalogRow[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>("title");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .catalog(debounced.trim())
      .then((res) => {
        if (cancelled) return;
        setRows(res);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        toast.error("Couldn't load catalog", { description: err.message });
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [debounced, refreshNonce]);

  const sorted = useMemo(() => {
    if (!rows) return rows;
    const copy = [...rows];
    copy.sort((a, b) => {
      const va = a[sortKey] ?? "";
      const vb = b[sortKey] ?? "";
      if (typeof va === "number" && typeof vb === "number") {
        return sortDir === "asc" ? va - vb : vb - va;
      }
      return sortDir === "asc"
        ? String(va).localeCompare(String(vb))
        : String(vb).localeCompare(String(va));
    });
    return copy;
  }, [rows, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search title, genre, keyword…"
            className="pl-9"
          />
        </div>
        <div className="text-xs text-muted-foreground">
          {sorted ? `${sorted.length} item${sorted.length === 1 ? "" : "s"}` : ""}
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading && !rows ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !sorted || sorted.length === 0 ? (
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              No catalog items match
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <SortableHead label="ID" k="id" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} className="w-20" />
                  <SortableHead label="Title" k="title" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                  <SortableHead label="Kind" k="kind" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} className="w-28" />
                  <SortableHead label="Genres" k="genres" sortKey={sortKey} sortDir={sortDir} onSort={toggleSort} />
                  <TableHead className="w-28">Image URL</TableHead>
                  <TableHead className="w-28">Poster data</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sorted.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      #{row.id}
                    </TableCell>
                    <TableCell className="font-medium">{row.title}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{row.kind}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {(row.genres || "")
                          .split(",")
                          .map((g) => g.trim())
                          .filter(Boolean)
                          .slice(0, 4)
                          .map((g) => (
                            <Badge key={g} variant="outline" className="font-normal">
                              {g}
                            </Badge>
                          ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusDot ok={row.has_image_url} okLabel="yes" missingLabel="missing" />
                    </TableCell>
                    <TableCell>
                      <StatusDot ok={row.has_poster_data} okLabel="yes" missingLabel="missing" />
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

interface SortableHeadProps {
  label: string;
  k: SortKey;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
  className?: string;
}

function SortableHead({ label, k, sortKey, sortDir, onSort, className }: SortableHeadProps) {
  const active = sortKey === k;
  const Icon = active ? (sortDir === "asc" ? ArrowUp : ArrowDown) : ArrowUpDown;
  return (
    <TableHead className={className}>
      <Button
        variant="ghost"
        size="sm"
        className="-ml-2 h-7 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground hover:bg-muted"
        onClick={() => onSort(k)}
      >
        {label}
        <Icon className={cn("ml-1 h-3 w-3", active ? "text-foreground" : "text-muted-foreground")} />
      </Button>
    </TableHead>
  );
}

function StatusDot({
  ok,
  okLabel,
  missingLabel,
}: {
  ok: boolean;
  okLabel: string;
  missingLabel: string;
}) {
  return (
    <span className="inline-flex items-center gap-1.5 text-xs">
      <span
        className={cn(
          "h-2 w-2 rounded-full",
          ok ? "bg-success shadow-[0_0_0_2px_hsl(var(--success)/0.2)]" : "bg-destructive"
        )}
      />
      <span className={ok ? "text-success" : "text-destructive"}>
        {ok ? okLabel : missingLabel}
      </span>
    </span>
  );
}
