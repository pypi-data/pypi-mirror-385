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
        vvv = [i for i in str(matches[0][1]).split() if Path(i).name== target]
        if  vvv:
            return vvv[0]    
        # return str(matches[0][1]).split()[1].strip("'\"")
    # else:



def py_main():
    vvv = where('python.exe')
    if  vvv:
        # print(1,vvv) # set path 來源
        return vvv
    else:
        vvv = get_vs_exe("Environment","python.exe",winreg.HKEY_CURRENT_USER)
        if  vvv:
            # print(3,vvv) # reg HKEY_CURRENT_USER\Environment 來源    ----------HKCU\Environment
            return vvv
        else:
            print("END")
    


print(py_main())