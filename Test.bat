@echo OFF

echo:
:: CLEAN UP PREVIOUS REPORTS
echo:
echo #### Clean up junk files
del /f /q /s "%~dp0\Report\*.*"
del /f /q /s "%~dp0\TempData\*.*"
if exist "%~dp0\geckodriver.log" del /f /q /s "%~dp0\geckodriver.log"

:: FIST RUN TEST
echo:
echo #### First run tests
cmd /c pybot --listener "%~dp0\Libraries\PythonListener.py" -d "%~dp0\Report" -o output.xml "%~dp0\Testsuites"

:: LOGICAL CHECK FOR RERUN FAIL TEST
if errorlevel 1 goto DGTFO
echo:
echo #### All tests passed
exit /b
:DGTFO

:: SECOND RUN FOR FAIL TEST
echo:
echo #### Rerun failed tests
cmd /c pybot --listener "%~dp0\Libraries\PythonListener.py" -d "%~dp0\Report" -R "%~dp0\Report\output.xml" -o rerun.xml "%~dp0\Testsuites"

:: MERGE TEST RESULTS
echo:
echo #### Merge tests
cmd /c rebot -d "%~dp0\Report" -o output.xml --merge "%~dp0\Report\output.xml" "%~dp0\Report\rerun.xml"

echo:
echo #### Finished batch execution
pause