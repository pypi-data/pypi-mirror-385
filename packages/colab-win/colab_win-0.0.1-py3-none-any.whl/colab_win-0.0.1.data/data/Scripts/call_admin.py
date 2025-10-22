def call_admin(path):
    # -----------------------------
    # 檢查管理員權限
    # -----------------------------
    def is_admin():
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    # -----------------------------
    # 提升權限重新執行
    # -----------------------------
    def run_as_admin(params):
        import ctypes,sys
        python_exe = sys.executable
        # # params = " ".join([f'"{arg}"' for arg in sys.argv])
        # print("@ params ",params) # @ params  "C:\Users\moon-\AppData\Local\Programs\Python38\Scripts\colab" "-VS"  ##########################################
        # ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 0) ## 隱藏
        # # ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
        sys.exit(0)
    # 普通模式執行（非 runas）
    def run_as_user(params):
        import ctypes,sys
        python_exe = sys.executable
        # # params = " ".join([f'"{arg}"' for arg in sys.argv])
        # print("@ params ",params) # @ params  "C:\Users\moon-\AppData\Local\Programs\Python38\Scripts\colab" "-VS"  ######################################
        # # ctypes.windll.shell32.ShellExecuteW(None, None, python_exe, params, None, 1) ## 顯示
        # # ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
        ctypes.windll.shell32.ShellExecuteW(None,"open","cmd.exe",f'/k "{python_exe}" {params}', None, 1) ## 顯示
        sys.exit(0)

# ctypes.windll.shell32.ShellExecuteW(
#     None,
#     "open",
#     "cmd.exe",
#     f'/k "{python_exe}" {params}',
#     None,
#     1
# )


    if  is_admin():
        # print('\n[python call_admin.py]')
        run_as_user(path)
    else:
        # print('\n[python call_admin.py]')
        run_as_admin(path)

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


def admin(name = "管理者權限3.py"):
    # import pathlib;Path=pathlib.Path
    from pathlib import Path
    params = str(Path(__file__).parent / name )
    call_admin( params )



admin('管理者權限3.py')