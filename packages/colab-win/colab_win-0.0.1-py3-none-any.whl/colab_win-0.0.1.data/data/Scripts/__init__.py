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
    root_python =  os.path.join('.vscode','Scripts','python.exe')  ### 工作區_python???
    # os.system(f'{root_python} -m pip install ipykernel -q ')
    # print(11)
    # pip_install(root_python)
    #########
    # os.system(f'"{root_python}" -m ipykernel install  --user  --name  {name} --display-name "{name}"')
    import subprocess,re
    safe_name = re.sub(r'[^A-Za-z0-9._-]', '', name) or "kernel_default"  ### 排除中文的部分
    cmd = [root_python, "-m", "ipykernel", "install", "--user", "--name", safe_name, "--display-name", name]
    subprocess.run(cmd)
    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    # print("returncode:", result.returncode)

    # print(222)################ 沒辦法 防止 資料夾---有空白
    # print(f'"{root_python}" -m ipykernel install  --user  --name  {name} --display-name "{name}"')


    # # 原始python.exe
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
    if  len(sys.argv)>=2 and sys.argv[1] in ["-VS","-vs"]: 
   
            # ###################
            if  len(sys.argv)==3:
                vs_exe = sys.argv[2]
                #     print(f"⚠️  colab -VS [安裝路徑] ，尚未建置，請先設定！")
                import subprocess,os
                from pathlib import Path
                BL = True if Path(vs_exe).name in ["code.exe","Code.exe","code","Code"] else False
                vs_exe = os.path.join(Path(vs_exe).parent,'bin','code.cmd')
                if  BL and subprocess.call(f'"{vs_exe}" --version >nul 2>nul', shell=True) == 0:
                    print("✅ VSCode 路徑正確")
                    import os
                    from pathlib import Path
                    vvv = sys.argv[2]
                    os.system(f'setx vs_exe "{Path(vvv).parent}" >nul　2>nul') 
                    print(f"✅ \"vs_exe\" {Path(sys.argv[2]).parent}")
                else:
                    print("⚠️ VSCode 路徑錯誤")
            # ###################
            if  len(sys.argv)==2:
                from Scripts.REG_find3_VS  import  vs_main
                vs_exe = vs_main(f"✅ \"vs_exe\" ","vs_exe")

                from Scripts.REG_find3_VS  import  if_vscode,get_vs_exe
                if  if_vscode():
                    # print(222)

                    # get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE, is_check=True)
                    ######################################
                    # 管理者權限3.py 裡面使用到 os.getenv("vs_exe",...)
                    from Scripts.call_admin  import admin
                    admin('管理者權限3.py')
                    keybindings('vs_exe')
                    launch_json('vs_exe')
                # else:
                    # print(111)



    if  len(sys.argv)>=2 and sys.argv[1] in ["-PY","-py","-init","-INIT"]: 
        # ###################
        if  len(sys.argv)==3:
            import os
            from pathlib import Path
            vs_python = sys.argv[2]
            BL = True if Path(vs_python).name in ["python.exe","Python.exe","python","Python"] else False
      
            
            if  BL and  os.system(f'{vs_python} -V >nul　2>nul')==0:
                print("✅ vs_python 路徑正確")
                os.system(f'setx vs_python "{vs_python}" >nul　2>nul') 
                print(f"✅ \"vs_python\" {vs_python}")
                # ###########################################
                # ### 安裝---其實挺快
                # # os.system(f'{vs_python} -m venv --without-pip --system-site-packages .\\.vscode')
                # new_venv(vs_python)
                # if  os.path.isfile(os.path.join(".vscode","Scripts","activate.bat")):
                #     # print(111)
                #     old_name = os.path.join(".vscode","Scripts","activate.bat")
                #     new_name = os.path.join(".vscode","Scripts","activate-x.bat")
                #     os.rename(old_name, new_name)
                #     print(f"✅ 已將檔案重新命名：{old_name} → {new_name}")

                # # os._exit(0) ###### 中斷---會無法輸出--- for /f %i in ('colab --ppp') do set vs_python=%i    
                # import sys
                # sys.exit(0)  ###### 可以輸出-- for /f %i in ('colab --ppp') do echo %i   
                # ###########################################
            else:
                print("⚠️ vs_python 路徑錯誤")

        # ###################
        if  len(sys.argv)==2 and sys.argv[1]=="-init":
            from Scripts.REG_find3_VS  import  vs_main
            vs_python = vs_main(f"✅ \"vs_python\" ","vs_python")  ### 取得----環境變數

            from Scripts.REG_find3_VS  import  if_vscode,get_vs_exe
            # if  if_vscode():
            #     # get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE, is_check=True)
            #     ######################################
            #     # 管理者權限3.py 裡面使用到 os.getenv("vs_exe",...)
            #     from Scripts.call_admin  import admin
            #     admin('管理者權限3.py')
            # ##########################
            # vs_python = os_getenv("vs_python")
            # if  not(os.path.isdir('.vscode/Scripts')):
            #     print('存在')
            ### 安裝---其實挺快
            # os.system(f'{vs_python} -m venv --without-pip --system-site-packages .\\.vscode')
            
            ####################################
            ##################################
            ### 建置 VM
            new_venv(vs_python)
            if  os.path.isfile(os.path.join(".vscode","Scripts","activate.bat")):
                # print(111)
                old_name = os.path.join(".vscode","Scripts","activate.bat")
                new_name = os.path.join(".vscode","Scripts","activate-x.bat")
                # print( os.path.isfile(new_name) )


                ####################################
                if  os.path.exists(new_name):
                    os.remove(new_name)  # 刪除舊檔案
                ####################################
                os.rename(old_name, new_name)
                print(f"✅ 已將檔案重新命名：{old_name} → {new_name}")
               
            # os._exit(0) ###### 中斷---會無法輸出--- for /f %i in ('colab --ppp') do set vs_python=%i    
            import sys
            sys.exit(0)  ###### 可以輸出-- for /f %i in ('colab --ppp') do echo %i  



    if  len(sys.argv)>=2 and sys.argv[1] in ["-http","-HTTP","-H","-h"]: 
        if  len(sys.argv)==2 and sys.argv[1] in ["-H","-h"] :
            # import requests
            # # 1️⃣ 縮網址
            # vvv_name = "Python社團"
            # short_url = f"http://bit.ly/{vvv_name}"

            # import requests
            # # 2️⃣ 取得最終真實 URL
            # # response = requests.head(short_url, allow_redirects=True)
            # # real_url = response.url
            # # print("真實 URL:", real_url)

            # # # 3️⃣ 下載檔案
            # # file_name = real_url.split("/")[-1]  # 從 URL 取檔名
            # # r = requests.get(real_url, stream=True)

            # # with open(  f"{file_name}.ipynb" , "wb") as f:
            # #     for chunk in r.iter_content(chunk_size=8192):
            # #         f.write(chunk)

            # # print(f"✅ 已下載 {file_name}.ipynb") 
            # #############################################
            # # 取得最終 URL
            # r = requests.head(short_url, allow_redirects=True)
            # real_url = r.url

            # # 嘗試從 Content-Disposition 取得檔名
            # file_name = None
            # cd = r.headers.get("Content-Disposition")
            # if cd and "filename=" in cd:
            #     file_name = cd.split("filename=")[-1].strip('\"')
            # else:
            #     from urllib.parse import unquote
            #     print(real_url)
            #     # fallback: 從 URL 最後一段取得檔名
            #     file_name = unquote(real_url.split("/")[-1])

            # ##################################################
            # # 將不合法字元替換掉
            # import re
            # file_name = re.sub(r'[\\/:*?"<>|]', "_", file_name)
            # # 如果沒有副檔名，可以補上 .bin 或其他你要的
            # if "." not in file_name:
            #     file_name += ".ipynb"
            # print("下載檔名:", file_name) ## # .ipynb
            # ########################################################
            # r = requests.get(real_url, stream=True)
            # with open(file_name, "wb") as f:
            #     for chunk in r.iter_content(chunk_size=8192):
            #         f.write(chunk)
            # print("✅ 下載完成")

            # import requests
            # from urllib.parse import urlparse, parse_qs
            # import re

            # # 1️⃣ bit.ly 縮網址
            # vvv_name = "Python社團"
            # short_url = f"http://bit.ly/{vvv_name}"

            # # 2️⃣ 取得最終跳轉 URL
            # r = requests.head(short_url, allow_redirects=True)
            # real_url = r.url
            # print("最終 URL:", real_url)

            # # 3️⃣ 從 Google Drive 分享連結取得檔案 ID
            # file_id = None

            # # 常見格式: https://drive.google.com/file/d/<file_id>/view?usp=sharing
            # m = re.search(r'/d/([a-zA-Z0-9_-]+)', real_url)
            # if m:
            #     file_id = m.group(1)
            # else:
            #     # 另一種可能格式 ?id=<file_id>
            #     parsed = urlparse(real_url)
            #     qs = parse_qs(parsed.query)
            #     if 'id' in qs:
            #         file_id = qs['id'][0]

            # if not file_id:
            #     raise ValueError("無法解析 Google Drive 檔案 ID")

            # https://colab.research.google.com/drive/1gkTR7iG5apv27mtlCyngdXgPQb_Ta3Je?usp=sharing
            file_id =r"1gkTR7iG5apv27mtlCyngdXgPQb_Ta3Je"
            # 4️⃣ 生成可直接下載的連結
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            print("可下載連結:", download_url)

            # 5️⃣ 嘗試下載檔案
            import requests
            file_name = "Python社團.ipynb"
            r = requests.get(download_url)
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(r.text)

            print(f"✅ 已下載 {file_name}")


       





if __name__ == "__main__":
    main()
