
# -----------------------------
# 提升權限重新執行
# -----------------------------
def run_as_admin():
    import ctypes,sys
    python_exe = sys.executable
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
    sys.exit(0)
# -----------------------------
# 建立 key 路徑
# -----------------------------
def create_key_if_not_exist(root, path):
    import winreg
    parts = path.split("\\")
    for i in range(len(parts)):
        sub_path = "\\".join(parts[:i+1])
        try:
            winreg.OpenKey(root, sub_path, 0, winreg.KEY_READ).Close()
        except FileNotFoundError:
            winreg.CreateKey(root, sub_path)


def set_icon(key_name="VSCode"):
    import os,sys,winreg
    import pathlib.Path as Path 
    # icon 路徑
    vs_root = Path(os.getenv(os_name)).parent
    icon_path = os.path.join(sys.exec_prefix, "vscode_win", "VS.ico")
    # 註冊表路徑
    reg_icon = rf"SOFTWARE\Classes\Folder\shell\{key_name}\Icon"

    try:
        # 開啟或建立註冊表鍵
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_icon) as key:
            # 設定預設值為 icon_path
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, icon_path)
        print(f"[OK] 設定圖示 {icon_path}")
    except PermissionError:
        print("[ERROR] 權限不足，請以管理員執行程式")

# -----------------------------
# 寫入註冊表
# -----------------------------
def set_vscode_registry(os_name):
    import os,sys,winreg
    # -----------------------------
    # 配置 VSCode 路徑
    # -----------------------------
    # value = f'"{vscode_exe}"  "%L"'
    from pathlib import Path
    vs_root = Path(os.getenv(os_name)).parent
    # 動態生成路徑 
    vscode_exe = os.path.join( vs_root, "vscode_win", "Code.exe")
    user_data_dir = os.path.join( vs_root, "vscode_win", "settings","user_data_dir")
    extensions_dir = os.path.join( vs_root, "vscode_win", "settings","extensions_dir")
    # reg_key = rf'HKCR\Folder\shell\{key_name}'
    reg_key = r'HKLM\SOFTWARE\Classes\Folder\shell\VSCode'   
    # 新增右鍵命令
    value = cmd = (
        rf'"{vscode_exe}" '
        rf'--user-data-dir="{user_data_dir}" '
        rf'--extensions-dir="{extensions_dir}" '
        r'"%L"'  # 右鍵選的資料夾
    )

    # 註冊表路徑
    key_path = r"SOFTWARE\Classes\Folder\shell\VSCode\command"
    try:
        ## 建立
        create_key_if_not_exist(winreg.HKEY_LOCAL_MACHINE, key_path)
        ## 開啟
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value)
        print("✅ 已成功設定 VSCode 右鍵開啟資料夾指令！")
    except PermissionError:
        # print("❌ 權限不足，需要管理員權限！")
        run_as_admin()

###########################
###########################
set_vscode_registry("vs_exe") ## ADD !!