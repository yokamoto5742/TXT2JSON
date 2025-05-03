import subprocess
import os
from version_manager import update_version, update_version_py


def build_executable():
    new_version = update_version()
    update_version_py(new_version)

    subprocess.run([
        "pyinstaller",
        "--name=TXT2JSON",
        "--windowed",
        "--icon=assets/TXT2JSON.ico",
        "main.py"
    ])

    # utils/config.ini をコピーして_internalに入れる。C:\Shinseikai\TXT2JSONに実行ファイルを移動。

    print(f"Executable built successfully. Version: {new_version}")


if __name__ == "__main__":
    build_executable()
