del /F /Q /S release
mkdir nightly
mkdir release
mkdir release\lib
mkdir release\bin
mkdir release\converted
mkdir release\db
mkdir release\db\episodes
mkdir release\download
mkdir release\import

copy dist\Valerie.jar release\
copy dist\lib release\lib\

copy bin\convert.exe release\bin\
copy bin\jpeg2yuv.exe release\bin\
copy bin\mencoder.exe release\bin\
copy bin\mpeg2enc.exe release\bin\
copy bin\pngquant.exe release\bin\
copy valerie.properties release\
copy replacements.txt release\

REM Get Revision
set /p REV=<"REV"

REM bin\7za.exe a -tzip nightly\valerie.zip release\*
bin\7za.exe a -tzip nightly\valerie_pc_rev%REV%.zip release\*

set PYTHON="E:\Python26\python.exe"
%PYTHON% upload.py
