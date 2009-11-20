set REPO="E:\Documents\Valerie\pc"
set SVN="E:\SlikSvn\bin\"


%SVN%svn up %REPO%

%SVN%svn status %REPO%

REM get REVISION
%SVN%svn status %REPO% > tmp.txt
 set /p REV=< tmp.txt

DEL tmp.txt

REM %REV%

REM build.bat

REM set PYTHON="E:\Python26\\python.exe"

REM %PYTHON% cron.py