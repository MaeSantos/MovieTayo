import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/components/theme-provider';
import { Moon, Sun, LogOut, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function Topbar() {
  const { logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const { refetch } = useQuery({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
    enabled: false,
  });

  const handleRefresh = () => {
    refetch();
    window.location.reload();
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-end gap-4 px-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          title="Refresh all data"
        >
          <RefreshCw className="h-5 w-5" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title="Toggle theme"
        >
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={logout}
          title="Lock / Sign out"
        >
          <LogOut className="h-5 w-5" />
        </Button>
      </div>
    </header>
  );
}
