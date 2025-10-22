# def     set_command(key_name = "VSCode2"):
#         import subprocess
#         # reg_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\VSCode\command"
#         # cmd = r'"C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "C:\Path\To\YourScript.py" "%1"'
#         # # subprocess.run(f'REG ADD "{reg_key}" /ve /d "{cmd}" /f', shell=True, check=True)
#         # 動態生成路徑 
#         vscode_exe = os.path.join(sys.exec_prefix, "vscode_win", "Code.exe")
#         user_data_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","user_data_dir")
#         extensions_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","extensions_dir")
#         # reg_key = rf'HKCR\Folder\shell\{key_name}'
#         # key_name = "VSCode2"
#         reg_key = rf'HKLM\SOFTWARE\Classes\Folder\shell\{key_name}'   
#         # 新增右鍵命令
#         cmd = (
#             rf'"{vscode_exe}" '
#             rf'--user-data-dir="{user_data_dir}" '
#             rf'--extensions-dir="{extensions_dir}" '
#             r'"%L"'  # 右鍵選的資料夾
#         )
#         # subprocess.run(f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f', shell=True, check=True)
#         # print(f"[Registry] 新增右鍵註冊: {reg_key}")
#         return f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f'

# def     set_Icon(key_name = "VSCode"):
#         import subprocess,sys
#         # icon_path = r"C:\Users\moon-\AppData\PythonAPI\Lib\site-packages\VScode_bin\VS.ico"
#         icon_path = os.path.join(sys.exec_prefix, "vscode_win", "VS.ico")
#         reg_icon = f"HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\Folder\\shell\\{key_name}\\Icon"
#         # subprocess.run(f'REG ADD "{reg_icon}" /ve /d "{icon_path}" /f', shell=True, check=True)
#         return f'REG ADD "{reg_icon}" /ve /d "{icon_path}" /f'


# import ctypes
# import sys
# import subprocess
# import os

# # -----------------------------
# # 檢查管理員權限
# # -----------------------------
# def is_admin():
#     import ctypes
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except:
#         return False
# # -----------------------------
# # 提升權限重新執行
# # -----------------------------
# def run_as_admin():
#     import ctypes,sys
#     python_exe = sys.executable
#     params = " ".join([f'"{arg}"' for arg in sys.argv])
#     # ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 0)
#     sys.exit(0)




# def set_vscode_registry(vscode_path, user_data_dir, extensions_dir, key_name="VSCode"):
#     """
#     刪除舊右鍵註冊，新增帶 --user-data-dir 和 --extensions-dir 的右鍵
#     """
#     run_as_admin()

#     reg_key = rf'HKCR\Folder\shell\{key_name}'
#     # 刪除舊鍵
#     subprocess.run(f'REG DELETE "{reg_key}" /f', shell=True,
#                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     print(f"[Registry] 刪除舊鍵: {reg_key}（若存在）")

#     # 新增右鍵命令
#     cmd = (
#         rf'"{vscode_path}" '
#         rf'--user-data-dir="{user_data_dir}" '
#         rf'--extensions-dir="{extensions_dir}" '
#         r'"%L"'  # 右鍵選的資料夾
#     )
#     # subprocess.run(f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f', shell=True, check=True)
#     # print(f"[Registry] 新增右鍵註冊: {reg_key}")
#     return f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f'

# if __name__ == "__main__":
#     # 動態生成路徑 
#     vscode_exe = os.path.join(sys.exec_prefix, "vscode_win", "Code.exe")
#     user_data_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","user_data_dir")
#     extensions_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","extensions_dir")

#     set_vscode_registry(vscode_exe, user_data_dir, extensions_dir)

def UU(os_name):
    # # -----------------------------
    # # 檢查管理員權限
    # # -----------------------------
    # def is_admin():
    #     import ctypes
    #     try:
    #         return ctypes.windll.shell32.IsUserAnAdmin()
    #     except:
    #         return False
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
    set_vscode_registry(os_name) ## ADD !!
    

# # print(999999999999999999)
# def UU(os_name):
#     # -----------------------------
#     # 檢查管理員權限
#     # -----------------------------
#     def is_admin():
#         import ctypes
#         try:
#             return ctypes.windll.shell32.IsUserAnAdmin()
#         except:
#             return False
#     # -----------------------------
#     # 提升權限重新執行
#     # -----------------------------
#     def run_as_admin():
#         import ctypes,sys
#         python_exe = sys.executable
#         params = " ".join([f'"{arg}"' for arg in sys.argv])
#         # ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 1)
#         ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, params, None, 0)
#         sys.exit(0)


#     def     set_command(key_name = "VSCode2"):
#             import subprocess,os,sys
#             # reg_key = r"HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\VSCode\command"
#             # cmd = r'"C:\Users\moon-\AppData\Local\Programs\Python38\python.exe" "C:\Path\To\YourScript.py" "%1"'
#             # # subprocess.run(f'REG ADD "{reg_key}" /ve /d "{cmd}" /f', shell=True, check=True)
#             # 動態生成路徑 
#             vscode_exe = os.path.join(sys.exec_prefix, "vscode_win", "Code.exe")
#             user_data_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","user_data_dir")
#             extensions_dir = os.path.join(sys.exec_prefix, "vscode_win", "settings","extensions_dir")
#             # reg_key = rf'HKCR\Folder\shell\{key_name}'
#             # key_name = "VSCode2"
#             reg_key = rf'HKLM\SOFTWARE\Classes\Folder\shell\{key_name}'   
#             # 新增右鍵命令
#             cmd = (
#                 rf'"{vscode_exe}" '
#                 rf'--user-data-dir="{user_data_dir}" '
#                 rf'--extensions-dir="{extensions_dir}" '
#                 r'"%L"'  # 右鍵選的資料夾
#             )
#             # subprocess.run(f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f', shell=True, check=True)
#             # print(f"[Registry] 新增右鍵註冊: {reg_key}")
#             return f'REG ADD "{reg_key}\command" /ve /d "{cmd}" /f'

#     def     set_Icon():
#             import subprocess,sys,os
#             # icon_path = r"C:\Users\moon-\AppData\PythonAPI\Lib\site-packages\VScode_bin\VS.ico"
#             icon_path = os.path.join(sys.exec_prefix, "vscode_win", "VS.ico")
#             reg_icon = r"HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Folder\shell\VSCode\Icon"
#             # subprocess.run(f'REG ADD "{reg_icon}" /ve /d "{icon_path}" /f', shell=True, check=True)
#             return f'REG ADD "{reg_icon}" /ve /d "{icon_path}" /f'

#     # #################################
#     # import os
#     # from pathlib import Path
#     # path = Path(os.getenv(os_name))  
#     # ################################
#     # vscode_exe =  path
#     # user_data_dir = path.parent / os.path.join("settings","user_data_dir")
#     # extensions_dir = path.parent /os.path.join("settings","extensions_dir")
#     # ################################
#     # # set_vscode_registry(vscode_exe, user_data_dir, extensions_dir)
#     # # if  run_as_admin():
#     # #     set_command(key_name = "VSCode")
#     # # return 6666
#     # ###########################
#     # # if  not(is_admin()):
#     # #     # print("⚠️ 尚未以管理員權限執行，正在重新啟動...")
#     # #     print("⚠️ 以管理員權限執行，正在重新啟動...")
#     # #     run_as_admin()
#     # #     ###########################
#     # #     ###########################


#     # import   subprocess   
#     # cmd =  set_vscode_registry(vscode_exe, user_data_dir, extensions_dir)+" && "+set_Icon()
#     # subprocess.run( cmd , shell=True, check=True)
#     ###########################
#     if  not(is_admin()):
#         # print("⚠️ 尚未以管理員權限執行，正在重新啟動...")
#         print("⚠️ 以管理員權限執行，正在重新啟動...")
#         run_as_admin()
#         ###########################
#         ###########################
#     import   subprocess   
#     cmd = set_command(key_name = "VSCode")+" && "+set_Icon()
#     subprocess.run( cmd , shell=True, check=True)
#     # import   subprocess   
#     # cmd =  set_vscode_registry(vscode_exe, user_data_dir, extensions_dir)+" && "+set_Icon()
#     # subprocess.run( cmd , shell=True, check=True)

