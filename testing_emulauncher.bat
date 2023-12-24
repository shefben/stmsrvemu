python -O ./emulator.py 

@echo off
echo Deleting all .pyo files recursively from the current directory...
del /s /q *.pyo 2>nul
echo Deletion complete.

@echo off
echo Deleting all .pyo files recursively from the current directory...
del /s /q *.pyc 2>nul
echo Deletion complete.

@echo off
echo Deleting subdirectories and files in files\temp...
for /d %%x in ("files\temp\*") do rd /s /q "%%x"
del /q "files\temp\*.*" 2>nul
echo Deletion complete for files\temp.

@echo off
echo Deleting subdirectories and files in files\cache...
for /d %%x in ("files\cache\*") do rd /s /q "%%x"
del /q "files\cache\*.*" 2>nul
echo Deletion complete for files\cache.

@echo off
echo Deleting all files from client\*...
for /d %%x in ("client\*") do rd /s /q "%%x"
del /s /q "client\*.*" 2>nul
echo Deletion complete for client.

@echo off
echo Deleting all __pycache__ directories recursively...
for /d /r . %%d in (__pycache__) do rd /s /q "%%d" 2>nul
echo Deletion complete for __pycache__ directories.
