import winreg

def reg_query(root, sub_key, search_str):
    matches = []

    def recursive_search(key, path):
        # 搜尋該 key 下所有值
        try:
            i = 0
            while True:
                name, value, _ = winreg.EnumValue(key, i)
                if search_str.lower() in str(value).lower():
                    matches.append((path, f"{name} = {value}"))
                i += 1
        except OSError:
            pass

        # 遞迴搜尋子鍵
        try:
            i = 0
            while True:
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{path}\\{subkey_name}"
                try:
                    subkey = winreg.OpenKey(key, subkey_name)
                    recursive_search(subkey, subkey_path)
                    subkey.Close()
                except PermissionError:
                    pass  # 有些鍵可能無權限
                i += 1
        except OSError:
            pass

    try:
        root_key = winreg.OpenKey(root, sub_key)
        recursive_search(root_key, sub_key)
        root_key.Close()
    except FileNotFoundError:
        pass

    return matches

if __name__ == "__main__":
    # reg query  HKEY_CLASSES_ROOT\vscode  /s /f  Code.exe
    results = reg_query(winreg.HKEY_CLASSES_ROOT, "vscode", "Code.exe")
    if results:
        for path, val in results:
            print(f"{path} -> {val}")
    else:
        print("沒有找到 Code.exe")

