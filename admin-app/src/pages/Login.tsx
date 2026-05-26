import { Eye, EyeOff, Film, Lock } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, api, setAdminToken } from "@/lib/api";

interface LoginProps {
  onSuccess: (token: string) => void;
}

export function Login({ onSuccess }: LoginProps) {
  const [token, setToken] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setAdminToken(token);
    try {
      await api.pingAuth();
      onSuccess(token);
    } catch (err) {
      setAdminToken("");
      if (err instanceof ApiError && err.status === 401) {
        setError("That token didn't unlock the admin API. Double-check and try again.");
      } else if (err instanceof Error) {
        setError(err.message || "Could not reach the admin API.");
      } else {
        setError("Could not reach the admin API.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden p-4">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_hsl(var(--primary)/0.25),_transparent_60%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 bg-[linear-gradient(180deg,_transparent,_hsl(var(--background)))]"
      />

      <Card className="w-full max-w-md animate-fade-in border-border/60 shadow-xl">
        <CardHeader className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow">
              <Film className="h-6 w-6" />
            </div>
            <div>
              <CardTitle className="text-lg">MovieTayo Admin</CardTitle>
              <CardDescription>
                Sign in with the admin token to manage your catalog.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="admin-token">Admin token</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="admin-token"
                  type={show ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="Enter admin token"
                  className="pl-9 pr-9"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  autoFocus
                  required
                />
                <button
                  type="button"
                  onClick={() => setShow((s) => !s)}
                  className="absolute right-2 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:bg-muted"
                  aria-label={show ? "Hide token" : "Show token"}
                >
                  {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <p className="text-xs text-muted-foreground">
                Default is <code className="rounded bg-muted px-1 py-0.5 text-[11px]">admin</code>;
                override with <code className="rounded bg-muted px-1 py-0.5 text-[11px]">MOVIETAYO_ADMIN_TOKEN</code>{" "}
                in your backend environment.
              </p>
            </div>

            {error && (
              <div
                role="alert"
                className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
              >
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Unlocking…" : "Unlock"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
