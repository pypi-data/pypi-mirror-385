import subprocess

vs_exe = r"C:\Users\moon-\AppData\Local\Programs\Python38\vscode_win\bin\code.cmd"    

if subprocess.call(f'"{vs_exe}" --version >nul 2>nul', shell=True) == 0:
    print("✅ VSCode 路徑正確")
else:
    print("⚠️ VSCode 路徑錯誤")
