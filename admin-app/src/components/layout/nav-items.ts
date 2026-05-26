import {
  BarChart3,
  Clapperboard,
  Flag,
  LayoutDashboard,
  type LucideIcon,
  Users,
} from "lucide-react";

export type PageKey = "dashboard" | "reports" | "users" | "catalog" | "behavior";

export interface NavItem {
  key: PageKey;
  label: string;
  description: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  {
    key: "dashboard",
    label: "Dashboard",
    description: "Overview & metrics",
    icon: LayoutDashboard,
  },
  {
    key: "reports",
    label: "Reports",
    description: "User-submitted reports",
    icon: Flag,
  },
  {
    key: "users",
    label: "Users",
    description: "Activity per user",
    icon: Users,
  },
  {
    key: "catalog",
    label: "Catalog",
    description: "Movies, series & anime",
    icon: Clapperboard,
  },
  {
    key: "behavior",
    label: "Behavior",
    description: "Interaction events",
    icon: BarChart3,
  },
];
