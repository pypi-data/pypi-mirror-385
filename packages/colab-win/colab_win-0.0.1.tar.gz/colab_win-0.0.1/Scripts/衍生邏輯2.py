import winreg

def query_registry_vscode():
    base_path = r"Folder\shell\VSCode"
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, base_path, 0, winreg.KEY_READ) as key:
            print(f"[OK] 開啟 {base_path}")

            # 只列出這一層的值，不往下遞迴
            index = 0
            while True:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, index)
                    print(f"🔹 {value_name} = {value_data}")
                    index += 1
                except OSError:
                    break

        print(f"📁 [END] 已完成：HKCR\\{base_path}")
    except FileNotFoundError:
        print(f"[!] 找不到：HKCR\\{base_path}")
    except PermissionError:
        print("[!] 權限不足，請以管理員執行")

if __name__ == "__main__":
    query_registry_vscode()
