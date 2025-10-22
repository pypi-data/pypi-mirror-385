####### 環境變數 Path
# @REM HKCU\Environment
# @REM  HKEY_CLASSES_ROOT\vscode
# @REM  HKEY_CLASSES_ROOT\vscode\shell\open\command

# @REM reg query HKEY_CLASSES_ROOT\Python.File /ve
# @REM HKEY_CLASSES_ROOT\Python.File
# @REM     (預設值)    REG_SZ    (數值未設定)
# @REM reg query HKEY_CLASSES_ROOT\Python.File\shell\open\command /ve
# @REM 錯誤: 系統找不到指定的登錄機碼或值。

# :: 先建立 ProgID 對應命令
ftype Python.File="C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "%1" %*
ftype Python.NoConFile="C:\Users\moon-\AppData\Local\Programs\Python38\pythonw.exe" "%1" %*

# :: 再把副檔名對應到 ProgID
assoc .py=Python.File
assoc .pyw=Python.NoConFile

ftype Python.File="C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "%1" %* && assoc .py=Python.File
ftype | find "Python.File"
reg query HKEY_CLASSES_ROOT\Python.File\shell\open\command /ve