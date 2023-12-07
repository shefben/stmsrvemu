python -O ./emulator.py 

@echo off
echo Deleting all .pyo files recursively from the current directory...
del /s /q *.pyo
echo Deletion complete.

@echo off
echo Deleting all .pyo files recursively from the current directory...
del /s /q *.pyc
echo Deletion complete.

echo Deleting subdirectories and files in files\temp...
for /d %%x in ("files\temp\*") do rd /s /q "%%x"
del /q "files\temp\*.*"
echo Deletion complete for files\temp.

echo Deleting subdirectories and files in files\cache...
for /d %%x in ("files\cache\*") do rd /s /q "%%x"
del /q "files\cache\*.*"
echo Deletion complete for files\cache.

echo Deleting all files from client\*...
for /d %%x in ("client\*") do rd /s /q "%%x"
del /s /q "client\*.*"
echo Deletion complete for client.
