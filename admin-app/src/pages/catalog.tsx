import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, RefreshCw, Image as ImageIcon, ArrowUpDown } from 'lucide-react';
import { useDebounce } from '@/lib/hooks';

interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

export function CatalogPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'id', direction: 'asc' });
  const debouncedSearch = useDebounce(searchQuery, 300);

  const { data: catalogData, isLoading, refetch } = useQuery({
    queryKey: ['catalog', debouncedSearch],
    queryFn: () => api.getCatalog(debouncedSearch),
    enabled: debouncedSearch.length === 0 || debouncedSearch.length >= 2,
  });

  const sortedItems = catalogData?.items?.sort((a, b) => {
    let aValue: any;
    let bValue: any;

    switch (sortConfig.key) {
      case 'id':
        aValue = a.id;
        bValue = b.id;
        break;
      case 'title':
        aValue = a.title;
        bValue = b.title;
        break;
      case 'content_type':
        aValue = a.content_type;
        bValue = b.content_type;
        break;
      case 'year':
        aValue = a.year;
        bValue = b.year;
        break;
      default:
        return 0;
    }

    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  }) || [];

  const handleSort = (key: string) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  if (isLoading && debouncedSearch.length >= 2) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Catalog</h1>
          <p className="text-muted-foreground">Search and manage your content library</p>
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Catalog</h1>
        <p className="text-muted-foreground">
          Search and manage your movie catalog
        </p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by title, genre, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
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
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {sortedItems.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => handleSort('id')}
                  >
                    <div className="flex items-center gap-2">
                      ID
                      <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => handleSort('title')}
                  >
                    <div className="flex items-center gap-2">
                      Title
                      <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => handleSort('content_type')}
                  >
                    <div className="flex items-center gap-2">
                      Type
                      <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => handleSort('year')}
                  >
                    <div className="flex items-center gap-2">
                      Year
                      <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </TableHead>
                  <TableHead>Genres</TableHead>
                  <TableHead>Poster</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-mono text-sm">#{item.id}</TableCell>
                    <TableCell className="font-medium">{item.title}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{item.content_type}</Badge>
                    </TableCell>
                    <TableCell>{item.year}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {item.genres.slice(0, 3).map((g, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {g.genre}
                          </Badge>
                        ))}
                        {item.genres.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{item.genres.length - 3}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {item.has_poster ? (
                        <Badge variant="success" className="gap-1">
                          <ImageIcon className="h-3 w-3" />
                          Yes
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="gap-1">
                          <ImageIcon className="h-3 w-3" />
                          No
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              {debouncedSearch.length >= 2
                ? 'No items match your search (try a shorter query)'
                : 'Enter at least 2 characters to search'}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
