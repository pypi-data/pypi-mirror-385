import winreg

def reg_query(root, key, target="Code.exe"):
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
        return str(matches[0][1]).split()[1].strip("'\"")

# for path, val in reg_query(winreg.HKEY_CLASSES_ROOT, "vscode"):
#     print(f"{path} -> {val}")

print(reg_query(winreg.HKEY_CLASSES_ROOT, "vscode" , "Code.exe"))