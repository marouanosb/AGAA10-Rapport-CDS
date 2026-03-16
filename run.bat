@echo off
REM ============================================================================
REM run.bat — AAGA10 CDS Project (Windows equivalent of Makefile)
REM
REM Usage:
REM   run.bat run → Run full benchmark suite + generate plots
REM   run.bat visualize → Visualize CDS on the small test instance
REM ============================================================================

if "%1"=="" goto experiments
if "%1"=="experiments" goto experiments
if "%1"=="visualize" goto visualize

echo Unknown command: %1
echo Usage: run.bat [experiments^|visualize]
goto end

:experiments
echo === Running full experiments ===
cd src
python run.py
cd ..
goto end

:visualize
echo === Visualizing CDS on small instance ===
cd src
python visualization.py test_instances/instance_small.json
cd ..
goto end

:end
