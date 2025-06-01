#Requires AutoHotkey v2.0 ; AutoHotkey v2.0 以降での実行を指示

; スクリプトの動作を安定させるためのおまじない
CoordMode "Mouse", "Screen" ; マウス座標をスクリーン全体を基準にする
A_DefaultMouseSpeed := 0    ; マウス移動を瞬時に行う (v2の記法)

; === mouseoperation.txt からの変換 ===
Click 0672, 0215 ; [cite: 1]
Click 1245, 0504 ; [cite: 1]
Click 0676, 0446 ; [cite: 1]
Click 0730, 0446 ; [cite: 1]
Click 0798, 0446 ; [cite: 1]
Click 0846, 0442 ; [cite: 1]
Click 0913, 0449 ; [cite: 1]
Click 0908, 0475 ; [cite: 1]
Click 0754, 0833 ; [cite: 1]
Click 1234, 0299 ; [cite: 1]
Click 1208, 0216 ; [cite: 1]
Click 0673, 0216 ; [cite: 1]

; スクリプトの終了
ExitApp()