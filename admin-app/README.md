# MovieTayo Admin - Modern SPA

A modern React-based Single Page Application for the MovieTayo admin dashboard, built with Vite, TypeScript, shadcn/ui, and PWA capabilities.

## 🚀 Features

- **Modern UI/UX**: Built with shadcn/ui components and Tailwind CSS
- **Responsive Design**: Mobile-first approach with collapsible sidebar
- **Dark/Light Theme**: Toggle between themes with persistence
- **PWA Support**: Installable as a desktop/mobile app
- **Real-time Data**: React Query for efficient data fetching and caching
- **Interactive Charts**: Beautiful visualizations with Recharts
- **Authentication**: Secure token-based auth with remember me option
- **Skeleton Loading**: Smooth loading states across all pages
- **Toast Notifications**: Rich feedback for user actions
- **Type-Safe**: Full TypeScript support

## 📁 Architecture

```
admin-app/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── app-shell.tsx    # Main layout wrapper
│   │   ├── sidebar.tsx      # Navigation sidebar
│   │   ├── topbar.tsx       # Header with actions
│   │   └── theme-provider.tsx # Theme management
│   ├── pages/
│   │   ├── login.tsx        # Authentication page
│   │   ├── dashboard.tsx    # Overview with charts
│   │   ├── reports.tsx      # User reports management
│   │   ├── users.tsx        # User management
│   │   ├── catalog.tsx      # Movie catalog with search
│   │   └── behavior.tsx     # User behavior analytics
│   ├── lib/
│   │   ├── api.ts           # API client with types
│   │   ├── auth.ts          # Auth state management
│   │   ├── formatters.ts    # Date/number utilities
│   │   ├── hooks.ts         # Custom React hooks
│   │   └── utils.ts         # General utilities
│   ├── App.tsx              # Main app with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/
│   ├── manifest.webmanifest # PWA manifest
│   ├── sw.js                # Service worker
│   └── Logo.png             # App icon
└── package.json
```

## 🛠️ Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI Library**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: React Query
- **Routing**: React Router v6
- **Charts**: Recharts
- **Notifications**: Sonner (Toast)
- **Icons**: Lucide React
- **PWA**: vite-plugin-pwa

## 📦 Installation

1. Navigate to the admin-app directory:
```bash
cd admin-app
```

2. Install dependencies:
```bash
npm install
```

## 🏃 Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000` with API proxy to the FastAPI backend on port 8001.

## 🏗️ Building

Build for production:
```bash
npm run build
```

The build output is emitted to the `../admin/` directory, which is served by the FastAPI backend at `/admin`.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the admin-app directory:

```env
VITE_API_BASE=/api
```

- `VITE_API_BASE`: Base URL for API requests (default: `/api` uses Vite proxy)

For production, you might want to set:
```env
VITE_API_BASE=https://your-backend-url.com/api
```

### Backend Integration

The admin app expects the following API endpoints (all under `/api/admin/`):

- `GET /stats` - Dashboard statistics
- `GET /reports?status=` - User reports with optional status filter
- `GET /users` - User list
- `GET /catalog?q=` - Catalog search
- `GET /behavior` - Behavior events
- `PATCH /reports/:id` - Update report status

### Authentication

The app uses token-based authentication via the `X-Admin-Token` header:
- Default token: `admin`
- Tokens are stored in localStorage (or sessionStorage if "Remember me" is unchecked)
- Token validation happens on login by fetching dashboard stats

## 🎨 UI/UX Features

### Dashboard
- **Metric Cards**: Animated counters for key statistics
- **Genre Distribution**: Interactive pie chart
- **Top Movies**: Bar chart with save counts
- **Trending List**: Ranked movie cards with save statistics

### Reports
- **Status Filtering**: Dropdown to filter by report status
- **Search**: Real-time search across all report fields
- **Inline Updates**: Change report status directly from table
- **Time Relative**: Human-readable timestamps

### Users
- **User Search**: Find users by name or email
- **Status Indicators**: Visual active/inactive badges
- **Summary Cards**: Quick stats for total, active, inactive users

### Catalog
- **Debounced Search**: Optimized search with 300ms delay
- **Sortable Columns**: Click headers to sort by any field
- **Genre Tags**: Visual genre badges with truncation
- **Poster Status**: Visual indicators for poster availability

### Behavior
- **Event Search**: Filter by user, action type, or content ID
- **JSON Context**: Expandable JSON viewer for event context
- **Time Formatting**: Relative time display

## 📱 PWA Features

The app is installable as a Progressive Web App:

- **Manifest**: `public/manifest.webmanifest`
- **Service Worker**: `public/sw.js` for offline caching
- **Installable**: Works on desktop (Chrome/Edge) and mobile
- **Theme Integration**: Respects system theme preferences

## 🎯 Design System

Built with shadcn/ui components following a consistent design system:

- **Colors**: HSL-based CSS variables for theming
- **Spacing**: Consistent scale (0.25rem increments)
- **Typography**: Inter font family with weight hierarchy
- **Radius**: Rounded corners with `--radius` CSS variable
- **Shadows**: Subtle elevation for depth

## 🧪 Testing

### Manual Testing Checklist

- [ ] Login with valid token
- [ ] Login with invalid token shows error
- [ ] Remember me functionality
- [ ] All dashboard metrics load correctly
- [ ] Charts render properly
- [ ] Navigation between pages works
- [ ] Sidebar collapses on mobile
- [ ] Theme toggle works
- [ ] Reports status filter works
- [ ] Report status update shows toast
- [ ] User search filters correctly
- [ ] Catalog search with debounce
- [ ] Catalog sorting works
- [ ] Behavior context viewer
- [ ] Refresh buttons work
- [ ] Logout redirects to login

### Browser Testing

Tested on:
- Chrome/Edge (Desktop & Mobile)
- Firefox (Desktop)
- Safari (Desktop & iOS)

## 🔒 Security Considerations

- Tokens are stored in localStorage/sessionStorage
- API requests include authentication header
- No sensitive data in URL parameters
- CSRF protection via token-based auth
- PWA service worker caches static assets only

## 🐛 Troubleshooting

### Build Issues

If you encounter build errors:

```bash
# Clear cache
rm -rf node_modules
npm install
npm run build
```

### API Connection Issues

If the app can't connect to the backend:

1. Check backend is running on port 8001
2. Verify Vite proxy configuration in `vite.config.ts`
3. Check `VITE_API_BASE` environment variable
4. Try setting `VITE_API_BASE` to full backend URL

### PWA Not Installing

1. Ensure app is served over HTTPS (required for PWA)
2. Check service worker is registered (DevTools → Application)
3. Verify manifest file is accessible
4. Try in incognito mode (extension conflicts)

## 📝 Development Notes

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add nav item in `src/components/sidebar.tsx`
4. Update API client in `src/lib/api.ts` if needed

### Adding UI Components

Use shadcn/ui patterns or create new components following the existing structure:
```typescript
// src/components/ui/your-component.tsx
import * as React from "react"
import { cn } from "@/lib/utils"

// Your component implementation
```

### Custom Hooks

Add custom hooks to `src/lib/hooks.ts`:
```typescript
export function useYourHook() {
  // Hook implementation
}
```

## 🚀 Deployment

### Production Build

```bash
cd admin-app
npm run build
```

The built files will be in `../admin/` and served by FastAPI at `/admin`.

### Environment Setup

For production, ensure:
1. `VITE_API_BASE` points to production backend
2. Backend has CORS enabled for the admin domain
3. PWA is served over HTTPS
4. Service worker is properly registered

## 📄 License

Same license as the main MovieTayo project.

## 🤝 Contributing

When contributing to the admin app:

1. Follow existing code style and patterns
2. Use TypeScript for all new code
3. Add appropriate error handling
4. Include loading states for async operations
5. Test on both desktop and mobile
6. Ensure accessibility (ARIA labels, keyboard nav)
