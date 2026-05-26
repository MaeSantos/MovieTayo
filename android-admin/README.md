# MovieTayo Admin App

This is the Android admin application for MovieTayo, providing a mobile interface for database management and analytics.

## Features

- Modern, responsive UI with glass-effect design
- Dashboard with real-time metrics
- User reports management
- User management interface
- Catalog search and management
- Behavior analytics
- Mobile-first design with bottom navigation
- Dark theme optimized for admin use

## Structure

```
android-admin/
├── app/
│   ├── build.gradle          # App-level build configuration
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── java/com/mae/movieadmin/
│           │   └── MainActivity.java
│           ├── assets/        # Admin interface files
│           │   ├── index.html
│           │   └── api-config.js
│           └── res/
│               ├── drawable/
│               │   └── ic_launcher.png
│               └── values/
│                   └── styles.xml
├── build.gradle              # Project-level build configuration
└── settings.gradle
```

## Requirements

- Android SDK 23+ (Android 6.0+)
- Java 17 or Java 21
- Gradle 8.0+
- Android Studio (recommended) or command-line build tools

## Building

### Using Android Studio (Recommended)

1. Open Android Studio
2. File → Open → Select the `android-admin` directory
3. Wait for Gradle sync to complete
4. Build → Build Bundle(s) / APK(s) → Build APK(s)
5. The APK will be in `app/build/outputs/apk/debug/app-debug.apk`

### Using Command Line

From the project root:

```bash
# Build the admin app
build_admin_app.bat

# Or with full backend and launch
start_admin_app.bat
```

### Manual Build

```bash
cd android-admin
gradle assembleDebug
```

## Installation

### On Connected Device/Emulator

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### Launch the App

```bash
adb shell am start -n com.mae.movieadmin/.MainActivity
```

## Configuration

The admin app uses the same backend as the main MovieTayo app.

### API Configuration

The admin interface reads API configuration from `app/src/main/assets/api-config.js`.

- For local development: Leave empty or set to local backend URL
- For remote access: Set `window.MOVIETAYO_API_BASE` to your backend URL

Example:
```javascript
window.MOVIETAYO_API_BASE = "https://your-backend-url.com";
```

### Admin Token

The app requires an admin token for authentication. The default token is `admin`.

To change the token:
1. Open the app
2. Enter your token in the authentication field
3. The token will be saved locally for future use

## Backend Integration

The admin app expects the following backend endpoints:

- `/api/admin/stats` - Dashboard metrics
- `/api/admin/reports` - User reports
- `/api/admin/users` - User management
- `/api/admin/catalog` - Catalog search
- `/api/admin/behavior` - Behavior analytics

Make sure your backend implements these admin routes with proper authentication.

## Development

### Modifying the Admin Interface

The admin interface is built with vanilla HTML/JS and Tailwind CSS. To modify:

1. Edit `admin/index.html` in the project root
2. The changes will automatically be included in the Android build (assets are linked)
3. Rebuild the APK to test changes

### Styling

The admin interface uses:
- Tailwind CSS (via CDN)
- Font Awesome icons
- Inter font family
- Custom glass-effect styling

### Testing

For local testing with Android emulator:

1. Start the backend: `run_backend.bat`
2. Set up port forwarding: `adb reverse tcp:8001 tcp:8001`
3. Install and launch the admin app

## Troubleshooting

### Build Issues

**Java Version Compatibility:**
- Ensure you're using Java 17 or Java 21
- Set `JAVA_HOME` environment variable appropriately
- If using Java 25+, you may need Gradle 8.5+ or use Android Studio

**Gradle Issues:**
- Use Android Studio for the most reliable builds
- Or ensure you have a compatible Gradle version in your PATH

**Sync Issues:**
- Delete `.gradle` folder in project root
- Invalidate caches in Android Studio
- Check internet connection for dependency downloads

### Runtime Issues

**API Connection:**
- Ensure backend is running
- Check `api-config.js` has correct URL
- For emulator, use `adb reverse tcp:8001 tcp:8001`
- For physical device, use ngrok or accessible IP

**Authentication:**
- Check admin token is correct
- Verify backend accepts the token
- Check browser console for authentication errors

## Differences from Main App

The admin app is separate from the main MovieTayo app:

- **Package ID**: `com.mae.movieadmin` (vs `com.mae.movieapp`)
- **App Name**: MovieTayo Admin (vs MovieTayo)
- **Interface**: Admin dashboard (vs user-facing movie app)
- **Functionality**: Management and analytics (vs browsing and recommendations)

## License

Same as the main MovieTayo project.
