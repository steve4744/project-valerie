del /F /Q /S release
mkdir nightly
mkdir release
mkdir release\lib
mkdir release\bin
mkdir release\converted
mkdir release\db
mkdir release\download

copy dist\Valerie.jar release\
copy dist\lib release\lib\

copy bin\mencoder.exe release\bin\
copy bin\pngquant.exe release\bin\
copy valerie.properties release\
bin\7za.exe a -tzip nightly\valerie.zip release\*