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



def vs_main(SS=f"✅ \"vs_exe\" "):
    vvv = where('Code.exe')
    if  vvv:
        print(1,vvv) # set path 來源
        return vvv
    else:
        vvv = get_vs_exe("Environment","Code.exe",winreg.HKEY_CURRENT_USER)
        if  vvv:
            print("Environment")
            # print(3,vvv)          # reg HKEY_CURRENT_USER\Environment 來源    ----------HKCU\Environment
            print(f'{SS} {vvv}')    # set path 改變 ---不會影響這邊
            return vvv
        else:
            vvv = get_vs_exe("vscode","Code.exe")
            # vvv = get_vs_exe("vscode","Code.exe",winreg.HKEY_CLASSES_ROOT)  reg HKEY_CLASSES_ROOT\vscode 來源
            if  vvv:
                # print(2,vvv) # reg HKEY_CLASSES_ROOT\vscode 來源        ----------HKCR\vscode
                print(f'{SS} {vvv}')
                return vvv
            else:
                print("END")
    


print(vs_main())
                
# HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\VSCode
# vvv = get_vs_exe("vscode","Code.exe",winreg.HKEY_LOCAL_MACHIN)



import winreg
from pathlib import Path

def get_vs_exe(key="vscode", target="Code.exe", root=winreg.HKEY_CLASSES_ROOT, is_check=False):
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

    # 如果只想檢查存在性
    if is_check:
        try:
            winreg.OpenKey(root, key)
            return True
        except FileNotFoundError:
            return False

    # 找 Code.exe
    if matches:
        vvv = [i for i in str(matches[0][1]).split() if Path(i).name == target]
        if vvv:
            return vvv[0]
    return None


# ✅ 範例：檢查是否存在
exists = get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE, is_check=True)
print("是否存在:", exists)

# ✅ 範例：搜尋 Code.exe 的路徑
path = get_vs_exe(key=r"SOFTWARE\Classes\Folder\shell\VSCode", root=winreg.HKEY_LOCAL_MACHINE)
print("VSCode 路徑:", path)
