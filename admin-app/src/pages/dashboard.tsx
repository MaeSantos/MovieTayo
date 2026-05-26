import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { formatNumber } from '@/lib/formatters';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import {
  Film,
  Users,
  Bookmark,
  Flag,
  Activity,
  ClipboardList,
  TrendingUp
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];

export function DashboardPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
  });

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Failed to load dashboard data</p>
      </div>
    );
  }

  const metrics = [
    {
      title: 'Catalog Items',
      value: stats!.catalog_items,
      icon: Film,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Users',
      value: stats!.users,
      icon: Users,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      title: 'Saved Items',
      value: stats!.saved_items,
      icon: Bookmark,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Open Reports',
      value: stats!.open_reports,
      icon: Flag,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
    {
      title: 'Behavior Events',
      value: stats!.behavior_events,
      icon: Activity,
      color: 'text-pink-500',
      bgColor: 'bg-pink-500/10',
    },
    {
      title: 'Total Reports',
      value: stats!.reports,
      icon: ClipboardList,
      color: 'text-cyan-500',
      bgColor: 'bg-cyan-500/10',
    },
  ];

  const genreData = stats!.top_genres.map((genre) => ({
    name: genre.genre,
    value: genre.count,
  }));

  const movieData = stats!.top_movies.slice(0, 5).map((movie) => ({
    name: movie.title.length > 20 ? movie.title.substring(0, 20) + '...' : movie.title,
    saves: movie.saved_count,
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {metric.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                  <Icon className={`h-4 w-4 ${metric.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(metric.value)}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Top Genres Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Genres</CardTitle>
          </CardHeader>
          <CardContent>
            {genreData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={genreData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {genreData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No genre data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Top Movies Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Movies</CardTitle>
          </CardHeader>
          <CardContent>
            {movieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={movieData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="saves" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No movie data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top Movies List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Trending Movies
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stats!.top_movies.length > 0 ? (
            <div className="space-y-4">
              {stats!.top_movies.map((movie, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{movie.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatNumber(movie.saved_count)} saves
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary">
                    {movie.saved_count} saves
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              No movies saved yet
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
