def init():
    import os
    vs_python = os.getenv('vs_python')
    print(vs_python)
    # # os.system(f'{vs_python} -m pip install ipykernel')
    # # 安裝 notebook 與 ipykernel，如果已安裝最新就不動
    # os.system(f'{vs_python} -m pip install notebook ipykernel --upgrade-strategy only-if-needed')

    # # root=os.path.join(os.getcwd(),'.vscode','Scripts')
    # root=os.path.join(os.getcwd(),'.venv','Scripts')
    # name=os.path.basename(os.getcwd())
    # if  not(os.path.isdir(root)):
    #     os.system(f'{vs_python} -m venv --without-pip --system-site-packages .\\.vscode')
    # # else:
    # os.system(f'jupyter kernelspec remove {name} -f')
    # root=os.path.join(os.getcwd(),'.venv','Scripts','python.exe')
    # os.system(f'{root} -m ipykernel install  --user  --name  {name} --display-name "{name}"')
    # # [out]
    # import subprocess; print(subprocess.run(['jupyter','kernelspec','list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout)



#   if  len(sys.argv)==3:
#                 if  sys.argv[1]=="--new":
#                     import os
#                     fff = os.path.join( sys.argv[2],".ipynb" ).replace(os.path.sep+'.',".")
#                     open(fff,'w').write('')
#                     print(f"🚀 新增 --new {fff} 被執行！")
    

def where(name_exe):
    import shutil
    return shutil.which(name_exe)
def os_getenv(name="vs_python"):
    import winreg
    key = r"Environment"  # 使用者層級
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as reg:
        value, _ = winreg.QueryValueEx(reg, name)
        print("從登錄檔讀取到 vs_python:", value)
        return value
def pip_install(vs_python):
    import subprocess, sys, time, shutil
    cmds = [
        # [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "-q"],
        # [sys.executable, "-m", "pip", "install", "jupyter", "ipykernel", "-q"],
        
        # [vs_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "-q"],
        # [vs_python, "-m", "pip", "install", "jupyter", "ipykernel", "-q"],

        [vs_python, "-m", "pip", "install", "ipykernel", "-q"],
    ]
    print("🛠️ 正在安裝套件...")
    for cmd in cmds:
        proc = subprocess.Popen(cmd)
        while proc.poll() is None:
            for i in range(0, 21):
                bar = "#" * i + "-" * (20 - i)
                print(f"\r[{bar}] 安裝中...", end="", flush=True)
                time.sleep(0.2)
            print("\r" + " " * shutil.get_terminal_size().columns, end="\r")
        print("\r✅ 完成！")
    print("🎉 所有套件安裝完畢！")


def new_venv(vs_python):
    import os
    # os.system(f'{vs_python} -m pip install ipykernel jupyter')
    # os.system(f'{vs_python} -m pip install --upgrade pip setuptools wheel -q ')
    # os.system(f'{vs_python} -m pip install jupyter ipykernel -q ')
    # pip_install(vs_python)

    root=os.path.join(os.getcwd(),'.vscode','Scripts')
    name=os.path.basename(os.getcwd())
    # if  not(os.path.isdir( root )):
        #1#
        # os.system(f'{vs_python} -m venv --without-pip --system-site-packages .\\.vscode')
        #2#
        # os.system(f'{vs_python} -m venv  --system-site-packages  .\\.vscode')  ## 可以加 pip list --local 只看 venv 自己的套件：
        # pass
        # pip list -l 或 pip list --local 是同一個意思的縮寫：

        
        #3#
        # os.system('curl https://bootstrap.pypa.io/get-pip.py -o .\\.vscode\\Scripts\get-pip.py')
        # runas /user:Administrator "F:\colab\.vscode\Scripts\python.exe -m ipykernel install --user --name colab --display-name colab"

        # os.system(f'{vs_python} -m venv --symlinks --without-pip --system-site-packages .\\.vscode')  ## --system-site-packages： --symlinks
    
    try:
        # os.system(f'{vs_python} -m venv  --system-site-packages  .\\.vscode')  ## 可以加 pip list --local 只看 venv 自己的套件：
        import subprocess,os
        result = subprocess.run(
        [vs_python, "-m", "venv", "--system-site-packages", ".\\.vscode"],
        check=True,               # 命令失敗時會拋出 CalledProcessError
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        print(result.stdout)
    except :
        print('當前 python.exe 正在使用 先關閉 vscode')
        os._exit(0)

    print("pwd ",os.getcwd() ,os.path.isdir( root ) ,root ,vs_python)
    # print( os.path.isdir(r'F:\colab\.vscode\Scripts')  )
    # else:
    os.system(f'jupyter kernelspec remove {name} -f >nul　2>nul')
    # print(f'jupyter kernelspec remove {name} -f >nul　2>nul')
    root_python =os.path.join(os.getcwd(),'.vscode','Scripts','python.exe')  ### 工作區_python???
    # os.system(f'{root_python} -m pip install ipykernel -q ')
    # print(11)
    # pip_install(root_python)
    os.system(f'{root_python} -m ipykernel install  --user  --name  {name} --display-name "{name}"')
    # print(f'{root_python} -m ipykernel install  --user  --name  {name} --display-name "{name}"')


    ## 原始python.exe
    # os.system(f'{vs_python} -m ipykernel install  --user  --name  {name} --display-name "{name}"')  

    # [out]
    import subprocess; print(subprocess.run(['jupyter','kernelspec','list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout)



def  keybindings(os_name='vs_exe'):
    import json
    from pathlib import Path

    keybindings = [
        {
            "key": "ctrl+r ctrl+y",
            "command": "workbench.action.reloadWindowWithExtensionsDisabled"
        },
        {
            "key": "ctrl+r ctrl+w",
            "command": "python.clearCacheAndReload"
        },
        # {
        #     "key": "f5",
        #     "command": "workbench.action.debug.start"
        # }
        {
            "key": "f5",
            "command": "workbench.action.debug.start",
            "when": "resourceExtname == .py"
        },
        {
            "key": "f5",
            "command": "workbench.action.terminal.sendSequence",
            "args": { "text": "${file}\u000D" },
            # "args": { "text": "echo ${file}\u000D" },
            # "args": { "text": "cd /d ${fileDirname} && ${fileBasename}\u000D" },
            # "args": { "text": "cd /d ${fileDirname} && ${fileBasename}\\u000D" },
            "when": "resourceExtname == .bat"
        }
    ]

    # 寫入 VSCode 全域 keybindings.json
    # path = Path.home() / "AppData/Roaming/Code/User/keybindings.json"
    import os
    path = Path(os.getenv(os_name))  
    # path.parent.mkdir(parents=True, exist_ok=True)
    file_name = path.parent / os.path.join("settings","user_data_dir","User","keybindings.json")
    # if  os.path.isfile(os.path.join(os.path.dirname(vs_exe),"settings","user_data_dir","User","keybindings.json")):
                # print(111)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(keybindings, f, ensure_ascii=False, indent=4)

    print(f"✅ 已寫入 {file_name}")


def launch_json(os_name='vs_exe'):
    import json
    from pathlib import Path

    launch ={
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Run Python",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",           #// 當前開啟的 .py
                    "console": "integratedTerminal"
                },
                {
                    "name": "Run Batch",
                    "type": "cppvsdbg",            #// 使用 Windows cmd
                    "request": "launch",
                    "program": "cmd.exe",
                    "args": ["/c", "${file}"],     #// 當前開啟的 .bat
                    "console": "integratedTerminal"
                }
            ],
            "compounds": [
                {
                    "name": "Run File",
                    "configurations": ["Run Python", "Run Batch"]
                }
            ]
    }


    # 寫入 VSCode 全域 keybindings.json
    # path = Path.home() / "AppData/Roaming/Code/User/keybindings.json"
    import os
    path = Path(os.getenv(os_name))  
    # path.parent.mkdir(parents=True, exist_ok=True)
    file_name = path.parent / os.path.join("settings","user_data_dir","User","launch.json")
    # if  os.path.isfile(os.path.join(os.path.dirname(vs_exe),"settings","user_data_dir","User","keybindings.json")):
                # print(111)
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump( launch, f, ensure_ascii=False, indent=4)

    print(f"✅ 已寫入 {file_name}")
    


# def add_reg(os_name):
#     import os
#     from pathlib import Path
#     path = Path(os.getenv(os_name))  
#     ################################
#     vscode_exe =  path
#     user_data_dir = path.parent / os.path.join("settings","user_data_dir")
#     extensions_dir = path.parent /os.path.join("settings","extensions_dir")
#     ################################
#     cmd = (
#         rf'"{vscode_exe}" '
#         rf'--user-data-dir="{user_data_dir}" '
#         rf'--extensions-dir="{extensions_dir}" '
#         r'"%L"'  # 右鍵選的資料夾
#     )
#     ################################################
#     import winreg
#     root = winreg.HKEY_LOCAL_MACHINE
#     path = r"SOFTWARE\Classes\Folder\shell\VSCode\command"
#     # cmd = r'"C:\Users\moon-\AppData\Local\Programs\Python38\vscode_win\Code.exe" "%L"'
#     # 自動建立路徑
#     with winreg.CreateKey(root, path ) as key:
#         winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)
#         print("✅ 已設定 registry command:", cmd)


# -----------------------------
# 寫入註冊表
# -----------------------------
# def set_vscode_registry(os_name):
    # import os,sys,winreg
    # # -----------------------------
    # # 配置 VSCode 路徑
    # # -----------------------------
    # # value = f'"{vscode_exe}"  "%L"'
    # # import pathlib;Path=pathlib.Path
    # from pathlib import Path
    # vs_root = Path(os.getenv(os_name)).parent
    # # 動態生成路徑 
    # vscode_exe = os.path.join( vs_root, "vscode_win", "Code.exe")
    # user_data_dir = os.path.join( vs_root, "vscode_win", "settings","user_data_dir")
    # extensions_dir = os.path.join( vs_root, "vscode_win", "settings","extensions_dir")
    # # reg_key = rf'HKCR\Folder\shell\{key_name}'
    # reg_key = r'HKLM\SOFTWARE\Classes\Folder\shell\VSCode'   
    # # 新增右鍵命令
    # value = cmd = (
    #     rf'"{vscode_exe}" '
    #     rf'--user-data-dir="{user_data_dir}" '
    #     rf'--extensions-dir="{extensions_dir}" '
    #     r'"%L"'  # 右鍵選的資料夾
    # )

    # # 註冊表路徑
    # key_path = r"SOFTWARE\Classes\Folder\shell\VSCode\command"
    # try:
    #     ## 建立
    #     create_key_if_not_exist(winreg.HKEY_LOCAL_MACHINE, key_path)
    #     ## 開啟
    #     with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
    #         winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value)
    #     print("✅ 已成功設定 VSCode 右鍵開啟資料夾指令！")
    # except PermissionError:
    #     # print("❌ 權限不足，需要管理員權限！")
    #     run_as_admin()

###########################
###########################
# set_vscode_registry(os_name) ## ADD !!


# Ctrl+R Ctrl+W 
# Reload Window
# Windows / Linux: Ctrl + K Ctrl + S
def main():
    import sys,os
    # if  os.getenv('VS_PYTHON'):
    if  len(sys.argv)>=2 and sys.argv[1]=="-VS": 
            # vs_exe =  where("Code.exe")
            # if  not(vs_exe) and  len(sys.argv)<3:
            #     print(f"⚠️  colab -VS [安裝路徑] ，尚未建置，請先設定！")
            #     os._exit(0)
            # elif    vs_exe:
            #         print(f"✅ \"vs_exe\" 　{vs_exe}")
            #         os.system(f'setx vs_exe "{vs_exe}" >nul　2>nul')
            # else:
            #     print(f"⚠️ set \"Path\" 找不到已安裝Code.exe!!") ### 應該跑不到這邊
            # # vs_python = os_getenv("vs_python")
            # ################
            if  len(sys.argv)==3:
                # import os

                # def test_vscode(vs_exe):
                #     cmd = f'cmd /c ""{vs_exe}" --version >nul 2>nul"'
                #     code = os.system(cmd)
                #     print(f"📦 測試命令：{cmd}")
                #     print(f"🔢 回傳值：{code}")
                #     return code == 0
                # test_vscode(vs_exe):
                vs_exe = sys.argv[2]
                #     print(f"⚠️  colab -VS [安裝路徑] ，尚未建置，請先設定！")
                import subprocess,os
                from pathlib import Path
                BL = True if Path(vs_exe).name in ["code.exe","Code.exe","code","Code"] else False
                vs_exe = os.path.join(Path(vs_exe).parent,'bin','code.cmd')
                if  BL and subprocess.call(f'"{vs_exe}" --version >nul 2>nul', shell=True) == 0:
                    print("✅ VSCode 路徑正確")
                else:
                    print("⚠️ VSCode 路徑錯誤")

                # if  os.system(f'{vs_exe} --version >nul 2>nul')==0 :
                #     print(f"✅ colab -VS [安裝路徑] 已成功建置，環境設定完成！")
                #     pass
                # else:
                #     print(f"⚠️  colab -VS [安裝路徑] ，尚未建置，請先設定！")
                
            if  len(sys.argv)==2:
                from Scripts.REG_find3_VS  import  vs_main
                vs_exe = vs_main(f"✅ \"vs_exe\" ")

                from Scripts.REG_find3_VS  import  if_vscode,get_vs_exe
                if  if_vscode():
                    # get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE, is_check=True)
                    ######################################
                    # 管理者權限3.py 裡面使用到 os.getenv("vs_exe",...)
                    from Scripts.call_admin  import admin
                    admin('管理者權限3.py')


            # # if  os.path.isfile(os.path.join(os.path.dirname(vs_exe),"settings","user_data_dir","User","keybindings.json")):
            # #     # print(111)
            # #     # open
            # keybindings('vs_exe')
            # launch_json('vs_exe')
            # # set_vscode_registry('vs_exe') ## ADD !!

         
            # # add_reg('vs_exe')
            # # import Scripts.新增REG  
            # # from Scripts.新增REG  import UU
            # # UU('vs_exe')
            # from Scripts.call_admin  import admin
            # admin('管理者權限3.py')

    if  len(sys.argv)>=2:
        if  sys.argv[1]=="-init":
            # os.system(f'setx vs_python "{vs_python}"')
            # if  os.getenv('vs_python'):
            #     pass
            # else:
            #     os.system(f'setx vs_python "" >nul')
            ###################################
            vs_python =  where("python.exe")
            if  vs_python:  ## 如果找不到 python.exe
                # if  len(sys.argv)==2:
                # if  len(sys.argv)==3: ### 使用 where
                print(vs_python)
                if  os.system(f'{vs_python} -V >nul　2>nul')==0:
                    print(f"✅ \"vs_python\" 　{vs_python}")
                    # if  os.path.isdir('.vscode'):
                        # print('目錄不存在')
                    # print(r'where python.exe :取到第一個索引  C:\Users\moon-\AppData\Local\Programs\Python38\python.exe')
                    os.system(f'setx vs_python "{vs_python}" >nul　2>nul')
                else:
                    print(f"⚠️ \"vs_python\" 路徑有問題！")
                    import os
                    os._exit(0)

                ### 建置::環境
                # new_venv(vs_python)
                
            # python -m venv --without-pip --system-site-packages .\.venv
            # else:
            if  True:
                # vs_python = os.getenv('vs_python')
                if  len(sys.argv)==2:
                    # print(777777777)
                    # print( os.getenv('vs_python') ,111) ## 根據 vs  變數 ----XXXXXXXXXX
                    # print(os_getenv("vs_python"),666)   ## 根據 reg 變數 ---------- 他會切空白  ---只取第一個
                    vs_python = os_getenv("vs_python")
                    # if  not(os.path.isdir('.vscode/Scripts')):
                    #     print('存在')
                    ### 安裝---其實挺快
                    # os.system(f'{vs_python} -m venv --without-pip --system-site-packages .\\.vscode')
                    new_venv(vs_python)
                    if  os.path.isfile(os.path.join(".vscode","Scripts","activate.bat")):
                        # print(111)
                        old_name = os.path.join(".vscode","Scripts","activate.bat")
                        new_name = os.path.join(".vscode","Scripts","activate-x.bat")
                        os.rename(old_name, new_name)
                        print(f"✅ 已將檔案重新命名：{old_name} → {new_name}")

                    # os._exit(0) ###### 中斷---會無法輸出--- for /f %i in ('colab --ppp') do set vs_python=%i    
                    import sys
                    sys.exit(0)  ###### 可以輸出-- for /f %i in ('colab --ppp') do echo %i   
                    ##################################################################
                    # "echo Hello VSCode! && echo %vs_python% && @for /f %i in ('colab --ppp') do @set VS_PYTHON=%i >nul 2>&1"
                    # @for /f %i in ('colab --ppp') do @set VS_PYTHON=%i >nul 2>&1" 
                    ##################################################################
                if  len(sys.argv)==3:
                    vs_python =  sys.argv[2].strip()
                    # print(f'{  vs_python }')
                    print()
                    if  os.system(f'{vs_python} -V >nul 2>nul')==0:
                        # print("Y ---222",vs_python)
                        # print(f"✅ 設置成功！ set vs_python={vs_python}")
                        print(f"✅ \"vs_python\" {vs_python} 路徑正確!!")
                        # os.environ['vs_python'] = vs_python
                        os.system(f'setx vs_python "{vs_python}"')
                    else:
                        # print("N ---222",vs_python)
                        print(f"⚠️ \"vs_python\" {vs_python}  路徑有問題!!")
                
    #     ##################################
    # if  len(sys.argv)==2:
    #     if  sys.argv[1]=="--init":
    #         if  "VS_PYTHON" in os.environ:
    #             import os
    #             vs_python = os.getenv('vs_python')
    #             # print(os.system(f'{vs_python} -V 2>nul'))  # Windows 隱藏錯誤輸出
    #             if  os.system(f'{vs_python} -V 2>nul')==0:
                
    #                 init()



    #             else:
    #                 print(f"⚠️ \"vs_python\" 路徑有問題！")
    #         else:
    #             print(f"⚠️  環境 \"VS_PYTHON\" 尚未建置，請先設定！")

    #     if  sys.argv[1]=="--VS":
    #         if  "VS" in os.environ:
    #             import os
    #             vs_exe = os.getenv('VS')
    #             # if  os.system(f'{vs_exe} -V 2>nul')==0:
    #                     # if  os.system(f'{vs_python} -V 2>nul')==0:
    #                     # else:
    #                     #     print(f"⚠️ \"vs_python\" 路徑有問題！")
                
    #         elif    where("Code.exe"):
    #                 vs_exe = where("Code.exe")
    #         else:
    #             print(f"⚠️  環境 \"VS\" 尚未建置，請先設定！")
    #             # where("Code.exe")
            
    # else:
    #     print(len(sys.argv))
    #     # print(f"🚀 新增 --new {fff} 被執行！")
    #     # if env_var not in os.environ:
       





if __name__ == "__main__":
    main()
