#Requires AutoHotkey v2.0 ; AutoHotkey v2.0 以降での実行を指示

; スクリプトの動作を安定させるためのおまじない
CoordMode "Mouse", "Screen" ; マウス座標をスクリーン全体を基準にする
A_DefaultMouseSpeed := 0    ; マウス移動を瞬時に行う (v2の記法)

; === soapcopy.txt からの変換 ===
Click 1222, 0300 ; [cite: 2]
Click 1799, 0013 ; [cite: 2]
Click 0929, 0423 ; [cite: 2]
SendInput "^a^c" ; [cite: 2]
Click 1271, 0258 ; [cite: 2]
Click 0807, 0427 ; [cite: 2]
SendInput "^a^c" ; [cite: 2]
Click 1271, 0258 ; [cite: 2]
Click 0807, 0427 ; [cite: 2]
SendInput "^a^c" ; [cite: 2]
Click 1271, 0258 ; [cite: 2]
Click 0807, 0427 ; [cite: 2]
SendInput "^a^c" ; [cite: 2]
Click 1271, 0258 ; [cite: 2]
Click 0807, 0427 ; [cite: 2]
SendInput "^a^c" ; [cite: 2]

; スクリプトの終了
ExitApp()