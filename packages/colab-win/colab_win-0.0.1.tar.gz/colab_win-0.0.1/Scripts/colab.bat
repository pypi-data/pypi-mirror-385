@echo off
REM 設定命令提示字元使用 UTF-8
@REM chcp 65001 >nul


REM 檢查第一個參數
if "%1"=="--new" (

) else if "%1"=="stop" (
    echo 停止程式
) else (
    echo 參數錯誤: %1
)



