@echo off
echo Starting MovieTayo Admin React App Dev Server...
echo.
echo Admin app will be available at: http://localhost:3000
echo API proxy: http://localhost:8001/api
echo.
cd admin-app
call npm run dev
cd ..
