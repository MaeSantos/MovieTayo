@echo off
echo Building MovieTayo Admin React App...
echo.
cd admin-app
call npm run build
cd ..
echo.
echo Admin React app build complete!
echo Build output: admin/ directory
echo.
