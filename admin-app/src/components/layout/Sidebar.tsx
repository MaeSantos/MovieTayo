import { Film } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS, type PageKey } from "./nav-items";

interface SidebarProps {
  active: PageKey;
  onChange: (page: PageKey) => void;
  collapsed?: boolean;
}

export function Sidebar({ active, onChange, collapsed = false }: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r bg-card/40 backdrop-blur-md transition-[width] duration-200",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div
        className={cn(
          "flex h-16 items-center gap-3 border-b px-4",
          collapsed && "justify-center px-0"
        )}
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
          <Film className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold">MovieTayo</span>
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Admin Console
            </span>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = item.key === active;
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onChange(item.key)}
              className={cn(
                "group flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary/15 text-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
                collapsed && "justify-center px-0"
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                className={cn(
                  "h-4 w-4 shrink-0",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {!collapsed && (
                <span className="flex flex-col text-left leading-tight">
                  <span className="font-medium">{item.label}</span>
                  <span className="text-[11px] text-muted-foreground">
                    {item.description}
                  </span>
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {!collapsed && (
        <div className="border-t p-3">
          <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
            Tip: install this site as an app from your browser's address bar for a
            full-screen admin experience.
          </div>
        </div>
      )}
    </aside>
  );
}
