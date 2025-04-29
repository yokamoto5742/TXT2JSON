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
        print("操作データをテキストファイルに保存し、そのファイル名をコマンドライン引数として指定してください。")
        print("例: python mouse_auto.py mouse_actions.txt")
    except Exception as e:
        print(f"エラー: {e}")

def run_from_hardcoded_data():
    actions_data = """実行までの時間,x座標,y座標,マウスの操作
0000,0672,0215,左ｸﾘｯｸ,
0002,1245,0504,左ｸﾘｯｸ,
0001,0676,0446,左ｸﾘｯｸ,
0000,0730,0446,左ｸﾘｯｸ,
0000,0798,0446,左ｸﾘｯｸ,
0000,0846,0442,左ｸﾘｯｸ,
0000,0913,0449,左ｸﾘｯｸ,
0000,0908,0475,左ｸﾘｯｸ,
0002,0754,0833,左ｸﾘｯｸ,
0002,1234,0299,左ｸﾘｯｸ,
0002,1208,0216,左ｸﾘｯｸ,
0002,0673,0216,左ｸﾘｯｸ,"""
    
    # データを行ごとに分割
    lines = actions_data.strip().split('\n')
    # ヘッダー行をスキップ
    if lines and "実行までの時間" in lines[0]:
        lines = lines[1:]
    
    run_actions(lines)

def run_actions(lines):
    try:
        print("3秒後に自動操作を開始します。緊急停止するには画面左上隅にマウスを移動してください。")
        time.sleep(3)  # 準備の時間
        
        for line in lines:
            # 空行をスキップ
            if not line.strip():
                continue
                
            # データをカンマで分割
            parts = line.strip().split(',')
            if len(parts) >= 4:  # 必要なデータがあることを確認
                wait_time = int(parts[0])
                x_coord = int(parts[1])
                y_coord = int(parts[2])
                action = parts[3]
                
                # 指定された時間だけ待機
                time.sleep(wait_time)
                
                # マウスを移動して操作を実行
                pyautogui.moveTo(x_coord, y_coord)
                
                # マウス操作の実行
                if "左ｸﾘｯｸ" in action:
                    pyautogui.click(button='left')
                elif "右ｸﾘｯｸ" in action:
                    pyautogui.click(button='right')
                elif "ﾀﾞﾌﾞﾙｸﾘｯｸ" in action:
                    pyautogui.doubleClick()
                
                print(f"実行: {wait_time}秒待機後、座標({x_coord}, {y_coord})で{action}")
        
        print("すべての操作が完了しました。")
    except Exception as e:
        print(f"エラー: {e}")

def main():
    # コマンドライン引数がある場合はファイルから実行、なければハードコードされたデータを使用
    if len(sys.argv) > 1:
        run_from_file(sys.argv[1])
    else:
        print("ファイル名が指定されていないため、ハードコードされたデータを使用します。")
        run_from_hardcoded_data()

if __name__ == "__main__":
    main()
