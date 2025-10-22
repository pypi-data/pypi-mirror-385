####################
def where(name_exe):
    import shutil
    return shutil.which(name_exe)
#####################
import winreg
def get_vs_exe(key="vscode", target="Code.exe",root=winreg.HKEY_CLASSES_ROOT):
    matches = []
    def search(k, path):
        try:
            # 搜尋值
            for i in range(winreg.QueryInfoKey(k)[1]):
                name, val, _ = winreg.EnumValue(k, i)
                if target.lower() in str(val).lower():
                    matches.append((path, f"{name} = {val}"))
            # 遞迴子鍵
            for i in range(winreg.QueryInfoKey(k)[0]):
                sub = winreg.EnumKey(k, i)
                try:
                    search(winreg.OpenKey(k, sub), f"{path}\\{sub}")
                except PermissionError:
                    continue
        except OSError:
            pass
    try:
        search(winreg.OpenKey(root, key), key)
    except FileNotFoundError:
        pass
    if  matches:
        # return str(matches)
        ####
        from pathlib import Path
        vvv = [i for i in str(matches[0][1]).split() if Path(i).name==  target ]
        if  vvv:
            return vvv[0]    
        # return str(matches[0][1]).split()[1].strip("'\"")
    # else:


########## 取得----環境變數
def vs_main(SS=f"✅ \"vs_exe\" ",os_name="vs_exe"):
    name = 'Code.exe' if os_name=="vs_exe" else ( 
           "python.exe"  if os_name=="vs_python" else "" )

    vvv = where( name ) 
    if  vvv:
        print(f'{SS} {vvv}') # set path 來源
        return vvv
    else:
        vvv = get_vs_exe("Environment",name ,winreg.HKEY_CURRENT_USER)
        if  vvv:
            # os.system(f'setx vs_python "{vs_python}" >nul　2>nul')
            # print("Environment")
            # print(3,vvv)          # reg HKEY_CURRENT_USER\Environment 來源    ----------HKCU\Environment
            print(f'{SS} {vvv}')    # set path 改變 ---不會影響這邊
            import os
            from pathlib import Path
            os.system(f'setx {os_name} "{Path(vvv).parent}" >nul　2>nul')
            return vvv
        else:
            #######################################
            ######################################  
            vvv = get_vs_exe("vscode","Code.exe")
            # vvv = get_vs_exe("vscode","Code.exe",winreg.HKEY_CLASSES_ROOT)  reg HKEY_CLASSES_ROOT\vscode 來源
            if  vvv:
                # print(2,vvv) # reg HKEY_CLASSES_ROOT\vscode 來源        ----------HKCR\vscode
                print(f'{SS} {vvv}')
                import os
                from pathlib import Path
                os.system(f'setx {os_name} "{Path(vvv).parent}" >nul　2>nul')
                return vvv
            else:
                print("END")
    


# print(vs_main())
                

# # 範例：檢查是否存在
# exists = get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE)
# print("是否存在:", exists)

# # HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\VSCode
# # vvv = get_vs_exe("vscode","Code.exe",winreg.HKEY_LOCAL_MACHIN)



def if_vscode(name="VSCode2"):
    import os
    return os.system(f'reg query "HKLM\\SOFTWARE\\Classes\\Folder\\shell\\{name}" /s >nul 2>&1')==0