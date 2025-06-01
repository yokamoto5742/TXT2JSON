import os
import subprocess

from utils.config_manager import load_config


def soap_copy():
    config = load_config()

    try:
        exe_path = config.get('Paths', 'soap_copy_file_path')
        if os.path.exists(exe_path):
            subprocess.run([exe_path], check=True)
        else:
            print(f"エラー: ファイルが見つかりません: {exe_path}")

    except subprocess.CalledProcessError as e:
        print(f"SOAPコピーEXE実行エラー: {e}")
    except Exception as e:
        print(f"SOAPコピーエラー: {e}")


def run_mouse_operation():
    config = load_config()

    try:
        exe_path = config.get('Paths', 'operation_file_path')
        if os.path.exists(exe_path):
            subprocess.run([exe_path], check=True)
        else:
            print(f"エラー: ファイルが見つかりません: {exe_path}")

    except subprocess.CalledProcessError as e:
        print(f"マウス操作EXE実行エラー: {e}")
    except Exception as e:
        print(f"マウス操作エラー: {e}")


def main(operation_type=None):
    if operation_type == "soap_copy":
        soap_copy()
    else:
        run_mouse_operation()
