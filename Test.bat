@echo OFF

echo:
:: CLEAN UP PREVIOUS REPORTS
echo:
echo #### Clean up junk files
del /f /q /s "%~dp0\Report\*.*"
del /f /q /s "%~dp0\TempData\*.*"
if exist "%~dp0\geckodriver.log" del /f /q /s "%~dp0\geckodriver.log"

:: INFO OF THIS BUILD
echo DEVKEY = '0962c90fda04f6ed0fcb39d87eb86e05' >"%~dp0\TestLink\TL_Exec_Info.txt"
echo PROJECT = 'NAP Special Delete' >>"%~dp0\TestLink\TL_Exec_Info.txt"
echo TESTPLAN = 'Demo RobotFramework TestPlan' >>"%~dp0\TestLink\TL_Exec_Info.txt"
echo TESTBUILD = 'Demo Build 1' >>"%~dp0\TestLink\TL_Exec_Info.txt"
echo RUNOWNER = 'Jane Dinh' >>"%~dp0\TestLink\TL_Exec_Info.txt"

:: FIST RUN TEST
echo:
echo #### First run tests
cmd /c pybot --listener "%~dp0\TestLink\TestLinkListener.py" -d "%~dp0\Report" -o output.xml "%~dp0\Testsuites"

:: LOGICAL CHECK FOR RERUN FAIL TEST
if errorlevel 1 goto DGTFO
echo:
echo #### All tests passed
exit /b
:DGTFO

:: SECOND RUN FOR FAIL TEST
echo:
echo #### Rerun failed tests
cmd /c pybot --listener "%~dp0\TestLink\TestLinkListener.py" -d "%~dp0\Report" -R "%~dp0\Report\output.xml" -o rerun.xml "%~dp0\Testsuites"

:: MERGE TEST RESULTS
echo:
echo #### Merge tests
cmd /c rebot -d "%~dp0\Report" -o output.xml --merge "%~dp0\Report\output.xml" "%~dp0\Report\rerun.xml"

echo:
echo #### Finished batch execution
pause