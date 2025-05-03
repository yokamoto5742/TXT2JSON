import time
import sys
import pyautogui

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
        print("指定されたパスにファイルが存在するか確認してください。")
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
                x_coord = int(parts[1])
                y_coord = int(parts[2])
                action = parts[3]

                time.sleep(wait_time)

                pyautogui.moveTo(x_coord, y_coord)

                if "左ｸﾘｯｸ" in action:
                    pyautogui.click(button='left')
                elif "右ｸﾘｯｸ" in action:
                    pyautogui.click(button='right')
                elif "ﾀﾞﾌﾞﾙｸﾘｯｸ" in action:
                    pyautogui.doubleClick()

    except Exception as e:
        print(f"エラー: {e}")


def main():
    operation_file_path = r"C:\Shinseikai\TXT2JSON\mouseoperation.txt"
    run_from_file(operation_file_path)


if __name__ == "__main__":
    main()
