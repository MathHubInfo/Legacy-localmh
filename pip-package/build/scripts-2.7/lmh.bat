@echo off
REM For windows, we need a batch file, so this does the same thing as the other file.
python -c "import lmh_core as lmh;lmh.main()" %*
exit /b %ERRORLEVEL%
