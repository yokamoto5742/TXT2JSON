import time
import re

import pyautogui

from utils.config_manager import load_config

pyautogui.FAILSAFE = True


def run_from_file(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if lines and "実行までの時間" in lines[0]:
            lines = lines[1:]

        run_actions(lines)

    except FileNotFoundError:
        print(f"エラー: ファイル '{file_name}' が見つかりません。")
    except Exception as e:
        print(f"エラー: {e}")


def run_actions(lines):
    try:
        for line in lines:
            if not line.strip():
                continue

            parts = line.strip().split(',')
            if len(parts) >= 4:
                wait_time = int(parts[0])
                action = parts[3]

                time.sleep(wait_time)

                if "ｷｰOnly" in action:
                    if len(parts) >= 5 and parts[4]:
                        key_sequence = parts[4]
                        keys = re.findall(r'\^[a-z]', key_sequence.lower())
                        for key in keys:
                            pyautogui.hotkey('ctrl', key[1])
                else:
                    x_coord = int(parts[1])
                    y_coord = int(parts[2])
                    pyautogui.moveTo(x_coord, y_coord)

                    if "左ｸﾘｯｸ" in action:
                        pyautogui.click(button='left')
                    elif "右ｸﾘｯｸ" in action:
                        pyautogui.click(button='right')
                    elif "ﾀﾞﾌﾞﾙｸﾘｯｸ" in action:
                        pyautogui.doubleClick()

    except Exception as e:
        print(f"エラー: {e}")

def soap_copy():
    config = load_config()
    try:
        soap_copy_file_path = config.get('Paths', 'soap_copy_file_path', fallback='soapcopy.txt')
        run_from_file(soap_copy_file_path)
    except Exception as e:
        print(f"SOAPコピーエラー: {e}")


def main(operation_type=None):
    if operation_type == "soap_copy":
        soap_copy()
    else:
        config = load_config()
        operation_file_path = config.get('Paths', 'operation_file_path')
        run_from_file(operation_file_path)


if __name__ == "__main__":
    main()