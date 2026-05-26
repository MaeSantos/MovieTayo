import { useCallback, useState } from "react";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { NAV_ITEMS, type PageKey } from "@/components/layout/nav-items";
import { Login } from "@/pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import { Reports } from "@/pages/Reports";
import { Users } from "@/pages/Users";
import { Catalog } from "@/pages/Catalog";
import { Behavior } from "@/pages/Behavior";
import { useAuth } from "@/store/auth";
import { useTheme } from "@/store/theme";
import { cn } from "@/lib/utils";

export function App() {
  const { isAuthenticated, login, logout } = useAuth();
  const { theme } = useTheme();
  const [page, setPage] = useState<PageKey>("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [refreshNonce, setRefreshNonce] = useState(0);

  const handleRefresh = useCallback(() => {
    setRefreshNonce((n) => n + 1);
  }, []);

  if (!isAuthenticated) {
    return (
      <>
        <Login onSuccess={login} />
        <Toaster theme={theme} richColors position="top-right" />
      </>
    );
  }

  const current = NAV_ITEMS.find((n) => n.key === page);

  return (
    <TooltipProvider delayDuration={150}>
      <div className="flex h-full min-h-screen w-full bg-background">
        {/* Desktop sidebar */}
        <div className="hidden md:block">
          <Sidebar active={page} onChange={setPage} />
        </div>

        {/* Mobile sidebar overlay */}
        <div
          className={cn(
            "fixed inset-0 z-30 bg-black/60 backdrop-blur-sm transition-opacity md:hidden",
            sidebarOpen ? "opacity-100" : "pointer-events-none opacity-0"
          )}
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
        <div
          className={cn(
            "fixed inset-y-0 left-0 z-40 transition-transform md:hidden",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          <Sidebar
            active={page}
            onChange={(p) => {
              setPage(p);
              setSidebarOpen(false);
            }}
          />
        </div>

        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar
            title={current?.label ?? "Dashboard"}
            subtitle={current?.description}
            onToggleSidebar={() => setSidebarOpen((v) => !v)}
            onRefresh={handleRefresh}
            onLogout={logout}
          />

          <main className="flex-1 overflow-y-auto p-4 md:p-6">
            {page === "dashboard" && <Dashboard refreshNonce={refreshNonce} />}
            {page === "reports" && <Reports refreshNonce={refreshNonce} />}
            {page === "users" && <Users refreshNonce={refreshNonce} />}
            {page === "catalog" && <Catalog refreshNonce={refreshNonce} />}
            {page === "behavior" && <Behavior refreshNonce={refreshNonce} />}
          </main>
        </div>
      </div>

      <Toaster theme={theme} richColors position="top-right" />
    </TooltipProvider>
  );
}
