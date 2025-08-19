@ECHO OFF
FOR /D %%G IN (data\train\*) DO (
    edf2asc %%G\%%~nxG
)

FOR /D %%G IN (data\test\*) DO (
    edf2asc %%G\%%~nxG
)