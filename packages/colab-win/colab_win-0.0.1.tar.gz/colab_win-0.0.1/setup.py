# def new_del_exe(dist="scripts", module=None):
#     import os, sys
#     ##############
#     if sys.platform.startswith("win"):
#         scripts_dir = os.path.join(sys.prefix, "Scripts")  # Windows
#     else:
#         scripts_dir = os.path.join(sys.prefix, "bin")      # Linux / macOS
#     # print(scripts_dir)
#     dist= scripts_dir
#     ###############
#     os.makedirs(dist, exist_ok=True)
#     m = f"{module}.egg-info" if module else ""
#     m = m.replace('-','_',1)
#     if sys.platform.startswith("win"):
#         script_name, content = f"{module}-y.bat", f"@echo off\nchcp 65001 >nul\nrd /s /q \"%CD%\\build\"\nrd /s /q \"%CD%\\{m}\"\necho [clean] 已刪除 build 和 {m}\npip uninstall {module} -y \ndel \"%~f0\"\n"
#     else:
#         script_name, content = f"{module}-y.sh", f"#!/bin/sh\nrm -rf \"%CD%\\build\"\nrm -rf \"%CD%\\{m}\"\necho '[clean] 已刪除 build 和 {m}'\npip uninstall {module} -y \nrm -- \"$0\"\n"
#     p = os.path.join(dist, script_name)
#     with open(p, "w", encoding="utf-8") as f: f.write(content)
#     if not sys.platform.startswith("win"): os.chmod(p, 0o755)
#     print(f"[setup] 已在 {dist} 生成 {script_name}")

def all_files(root_dir):
    import os
    data_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if filenames:
            # 安裝到相對於 site-packages 的相同路徑
            target_dir = os.path.join(root_dir, os.path.relpath(dirpath, root_dir))
            files = [os.path.join(dirpath, f) for f in filenames]
            data_files.append((target_dir, files))
    return data_files

def run_bdist_wheel():
    import os
    dist = os.path.join(os.getcwd(),"dist")
    ##  如果不存在目錄--才執行
    if  not os.path.isdir(dist):
        import atexit
        def after_setup():
            print("=== [這裡是避免變成迴圈] ===")
            import subprocess,os
            if os.environ.get("RUN_BDIST_WHEEL") == "1":
                print("=== [結束後執行函數] ===")
                ### 生成clean_build.py  
                # gen_clean_build("dist", "conda_win")

                ############################# call 函數
                # new_del_exe("dist", "colab" )  ### 新增--刪除檔案
            else:
                print("=== [結束後執行函數，但未呼叫 bdist_wheel] ===")
                # 複製當前環境變數
                env = os.environ.copy()
                env["RUN_BDIST_WHEEL"] = "1"  # 設定環境變數
                # 重新啟動 setup.py 執行 bdist_wheel
                # python setup.py bdist_wheel
                import subprocess
                subprocess.check_call([sys.executable, "setup.py", "bdist_wheel"], env=env)
                
        atexit.register(after_setup)



# Scripts
import sys
# 判斷當前階段
is_build = 'build_py' in sys.argv
is_wheel = 'bdist_wheel' in sys.argv
is_install = 'install' in sys.argv
data_files = []


if is_build:
    print("=== [BUILD_PY 階段] 建立中間檔案 ===")
elif is_wheel:        
    print("=== [BDIST_WHEEL 階段] 產生 wheel ===")
    
    
    # data_files = all_files("bin")
    data_files = all_files("Scripts")
    ### python setup.py bdist_wheel
    run_bdist_wheel()  ##############  會產生一份 .whi
   
    


   
# F:\conda-win\build\bdist.win-amd64
# F:\conda-win\conda_win.egg-info
elif is_install:

    print("=== [INSTALL 階段] 安裝 wheel 至 site-packages ===")

    data_files = all_files("bin")
    ### python setup.py bdist_wheel
    run_bdist_wheel()

    import os
    # vs_python = os.getenv('vs_python')
    # if  os.system(f'{vs_python} -V 2>nul')==0:

    os.system(f'python -c ""')


# twine upload -u __token__ -p <你的 token> dist/*
# twine upload -u __token__ -p %pypi% dist/*

from setuptools import setup
setup(
    name="colab-win",
    version="0.0.1",
    # entry_points={
    #     "console_scripts": [
    #         "clean_build=conda_win.clean_build:main",
    #     ]
    # },
    # Scripts = ["dist/clean_build.bat"] ,
    # scripts=["dict/conda-win.bat", "dict/conda-win.sh"],
    # scripts=["dict/conda-win.bat"],
    # packages=[],  # 可留空或指定實際模組

    # cmdclass={
    #     "bdist_wheel": CustomWheel,  # 這裡必須有 CustomWheel 定義
    # },



    #########  ..\..\Scripts\colab.bat
    Scripts = ["./Scripts/colab.bat","./Scripts/reg-find.bat","./Scripts/set-del.bat"] ,
    ######### 可以用來查看 檔案
    ######### pip show -f colab
    # packages   =  ['bin'], ## ,'Scripts'
    # packages   =  ['Scripts'], ## ,'Scripts'
    data_files =  data_files,



    
#     entry_points={
#         "console_scripts": [
#             "mycli=mypackage.main:main",
#         ],
#     },
    packages=[],

    ############## --target="./site-packages"
    ############## ./site-packages/bin/colab.exe"
    entry_points={
        "console_scripts": [
            "colab = Scripts:main",
        ],
    },


    # "C:\\Users\\moon-\\AppData\\PythonAPI\\Lib\\site-packages\\VS_pop\\Code.exe" --user-data-dir="C:\Users\moon-\AppData\PythonAPI\Lib\site-packages\VS_bin\settings"  --extensions-dir="C:\Users\moon-\AppData\PythonAPI\VSData\extensions2"  "%L"
    # "C:\Users\moon-\AppData\Local\Programs\Python38\vscode_win\Code.exe" --user-data-dir="C:\Users\moon-\AppData\Local\Programs\Python38\vscode_win\settings\user_data_dir" --extensions-dir="C:\Users\moon-\AppData\Local\Programs\Python38\vscode_win\settings\extensions_dir" "%L"
    # # 安裝選項
    # options={
    #     "install": {
    #         "install_lib": r"F:\colab\site_packages"  # 指定 site-packages 目錄
    #     }
    # }
    # 在 install 替他加上  ssys.argv 看看
    # pip install . --target "F:\colab\site-packages"

)

# python -m pip install . -v
# rm -rf build dist *.egg-info


# set path=C:\Users\moon-\AppData\Local\Programs\Python38;C:\Users\moon-\AppData\Local\Programs\Python38\Scripts;C:\Windows\System32;








# pip install <package_name> --target "C:\path\to\my_site_packages"
