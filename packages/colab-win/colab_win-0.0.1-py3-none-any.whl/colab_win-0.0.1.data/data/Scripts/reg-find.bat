@echo off

echo %*


if "%1"=="" (
    echo "Hello!"
    echo.reg-find.bat  HKCU\Environment  vs_exe
    echo.reg-find.bat  HKCU\Environment  vs_python
    
) else (

if "%2"=="" (
    reg query "HKCU" /s /f "%1"
) else (
    reg query "%1" /s /f "%2"
)

)



@REM HKCU\Environment
@REM  HKEY_CLASSES_ROOT\vscode
@REM  HKEY_CLASSES_ROOT\vscode\shell\open\command



@REM reg query HKEY_CLASSES_ROOT\Python.File /ve
@REM HKEY_CLASSES_ROOT\Python.File
@REM     (預設值)    REG_SZ    (數值未設定)
@REM reg query HKEY_CLASSES_ROOT\Python.File\shell\open\command /ve
@REM 錯誤: 系統找不到指定的登錄機碼或值。


@REM :: 先建立 ProgID 對應命令
@REM ftype Python.File="C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "%1" %*
@REM ftype Python.NoConFile="C:\Users\moon-\AppData\Local\Programs\Python38\pythonw.exe" "%1" %*

@REM :: 再把副檔名對應到 ProgID
@REM assoc .py=Python.File
@REM assoc .pyw=Python.NoConFile

@REM ftype Python.File="C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "%1" %* && assoc .py=Python.File
@REM ftype | find "Python.File"
@REM reg query HKEY_CLASSES_ROOT\Python.File\shell\open\command /ve


@REM ProgID ------------獲得 檔案路徑
@REM ftype | find "Python.File"
@REM ftype | find "Python"

@REM 檔案關聯 ------------ 獲得 Python.File ------ vscode 找不到
@REM ftype Python.File
@REM assoc | findstr Python