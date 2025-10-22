import winreg

roots = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
}
path = r"SOFTWARE\Classes\Folder\shell\VSCode"

for name, root in roots.items():
    try:
        with winreg.OpenKey(root, path) as key:
            print(f"✅ {name} 存在")
            try:
                cmd_key = winreg.OpenKey(root, path + r"\command")
                value, _ = winreg.QueryValueEx(cmd_key, "")
                print(f"   → 指令: {value}")
            except FileNotFoundError:
                print(f"   ⚠ 無 command 子鍵")
    except FileNotFoundError:
        print(f"❌ {name} 不存在")



# reg query "HKCU\SOFTWARE\Classes\Folder\shell\VSCode"
# reg query "HKLM\SOFTWARE\Classes\Folder\shell\VSCode"
# reg query "HKCR\Folder\shell\VSCode"
#################
# reg query "HKCU\SOFTWARE\Classes\Folder\shell\VSCode" /s | find "VSCode"
# reg query "HKLM\SOFTWARE\Classes\Folder\shell\VSCode" /s | find "VSCode"
# reg query "HKCR\Folder\shell\VSCode" /s | find "VSCode"