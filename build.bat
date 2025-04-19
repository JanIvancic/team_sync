@echo off
echo Building Vue app...
cd frontend\team_sync_front
call npm install
call npm run build
cd ..\..
echo Copying built files to static directory...
if not exist static mkdir static
xcopy /E /Y frontend\team_sync_front\dist\* static\
echo Build complete! 