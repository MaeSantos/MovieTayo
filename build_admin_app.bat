@echo off
echo Building MovieTayo Admin App...
echo.
echo Note: If you encounter Java version compatibility issues, make sure you have:
echo - Java 17 or Java 21 installed
echo - Gradle 8.0+
echo.
echo Attempting to build with system Gradle...
cd android-admin

REM Try multiple gradle locations
if exist "gradlew.bat" (
    echo Using gradlew wrapper...
    call gradlew.bat assembleDebug
) else if exist "%USERPROFILE%\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat" (
    echo Using user Gradle 8.14.3...
    call "%USERPROFILE%\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat" assembleDebug
) else if exist "C:\Users\Mae\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat" (
    echo Using local Gradle 8.14.3...
    call "C:\Users\Mae\.gradle\wrapper\dists\gradle-8.14.3-all\10utluxaxniiv4wxiphsi49nj\gradle-8.14.3\bin\gradle.bat" assembleDebug
) else (
    echo Trying system gradle...
    call gradle assembleDebug
)

cd ..
echo.
echo Admin app build process complete.
echo If successful, APK location: android-admin\app\build\outputs\apk\debug\app-debug.apk
echo.
echo If build failed due to Java compatibility, try:
echo 1. Set JAVA_HOME to Java 17 or 21
echo 2. Or use Android Studio: Open android-admin folder as project and build there
