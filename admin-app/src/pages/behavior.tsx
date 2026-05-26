import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { formatRelativeTime } from '@/lib/formatters';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Search, RefreshCw, Code, Eye, EyeOff } from 'lucide-react';

export function BehaviorPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedContext, setExpandedContext] = useState<number | null>(null);

  const { data: behaviorData, isLoading, refetch } = useQuery({
    queryKey: ['behavior'],
    queryFn: () => api.getBehavior(),
  });

  const filteredEvents = behaviorData?.events?.filter(event =>
    event.user_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.action_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.content_id.toString().includes(searchQuery)
  ) || [];

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">Behavior</h1>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="flex gap-4">
          <Skeleton className="h-10 flex-1" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Card>
          <CardContent className="p-0">
            <div className="space-y-4 p-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Behavior Analytics</h1>
          <p className="text-muted-foreground">
            Understand how users interact with your platform
          </p>
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by user, action type, or content ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {filteredEvents.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Content ID</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Context</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEvents.map((event) => (
                  <TableRow key={event.id}>
                    <TableCell className="font-mono text-sm">#{event.id}</TableCell>
                    <TableCell className="font-medium">{event.user_id}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{event.action_type}</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-sm">#{event.content_id}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatRelativeTime(event.timestamp)}
                    </TableCell>
                    <TableCell>
                      {event.context ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setExpandedContext(
                            expandedContext === event.id ? null : event.id
                          )}
                          className="gap-2"
                        >
                          <Code className="h-4 w-4" />
                          {expandedContext === event.id ? (
                            <>
                              <EyeOff className="h-3 w-3" />
                              Hide
                            </>
                          ) : (
                            <>
                              <Eye className="h-3 w-3" />
                              View
                            </>
                          )}
                        </Button>
                      ) : (
                        <span className="text-sm text-muted-foreground">None</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {expandedContext !== null && (
                  <TableRow>
                    <TableCell colSpan={6} className="p-4">
                      <div className="bg-muted p-4 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Code className="h-4 w-4" />
                          <span className="font-mono text-sm">
                            Context for event #{expandedContext}
                          </span>
                        </div>
                        <pre className="text-xs overflow-auto max-h-64">
                          {JSON.stringify(
                            filteredEvents.find(e => e.id === expandedContext)?.context,
                            null,
                            2
                          )}
                        </pre>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              {searchQuery
                ? 'No events match your search'
                : 'No behavior events recorded yet'}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
