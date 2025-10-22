@echo off

echo %*


if "%1"=="" (
    echo "Hello!"
    echo  reg delete "HKCU\Environment" /v vs_exe /f
    echo  set-del vs_exe
    
) else (

reg delete "HKCU\Environment" /v %1 /f

)



