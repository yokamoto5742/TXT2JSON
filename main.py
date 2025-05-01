import json
import os
import re
import subprocess
import sys
from io import StringIO

import pyperclip
import tkinter as tk
from tkinter import scrolledtext, messagebox

from services import mouse_automation
from services.txt_parse import parse_medical_text
from services.txt_editor import TextEditor


class MedicalTextConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON形式変換")
        self.root.geometry("1000x600")

        # クリップボード監視状態を管理する変数
        self.is_monitoring_clipboard = True

        # フレームの作成
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill=tk.BOTH, expand=True)

        # カルテ記載フレーム
        self.frame_karte = tk.LabelFrame(self.frame_top, text="カルテ記載")
        self.frame_karte.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # テキスト入力エリア
        self.text_input = scrolledtext.ScrolledText(self.frame_karte, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # JSON形式フレーム
        self.frame_json = tk.LabelFrame(self.frame_top, text="JSON形式")
        self.frame_json.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # JSON出力エリア
        self.text_output = scrolledtext.ScrolledText(self.frame_json, height=10)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 行数と文字数の表示
        self.frame_stats = tk.Frame(root)
        self.frame_stats.pack(fill=tk.X)

        self.stats_label = tk.Label(self.frame_stats, text="カルテ記載行数: 0  文字数: 0")
        self.stats_label.pack(side=tk.LEFT, padx=5, pady=5)

        # クリップボード監視状態の表示
        self.monitor_status_label = tk.Label(self.frame_stats, text="クリップボード監視: ON", fg="green")
        self.monitor_status_label.pack(side=tk.RIGHT, padx=5, pady=5)

        # ボタンフレーム
        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(fill=tk.X, pady=10)

        # 新規登録ボタン
        self.new_button = tk.Button(self.frame_buttons, text="新規登録",
                                    command=self.start_monitoring, width=15, height=2)
        self.new_button.pack(side=tk.LEFT, padx=10)

        # SOAP画面設定ボタン
        self.soap_button = tk.Button(self.frame_buttons, text="SOAP画面設定",
                                     command=self.run_mouse_automation, width=15, height=2)
        self.soap_button.pack(side=tk.LEFT, padx=10)

        # JSON変換ボタン
        self.convert_button = tk.Button(self.frame_buttons, text="JSON形式に変換",
                                        command=self.convert_to_json, width=15, height=2)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        # テキストクリアボタン
        self.clear_button = tk.Button(self.frame_buttons, text="テキストクリア",
                                      command=self.clear_text, width=15, height=2)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # テキストエディタボタン
        self.editor_button = tk.Button(self.frame_buttons, text="出力結果確認",
                                       command=self.open_text_editor, width=15, height=2)
        self.editor_button.pack(side=tk.LEFT, padx=10)

        # 閉じるボタン
        self.close_button = tk.Button(self.frame_buttons, text="閉じる",
                                      command=self.root.destroy, width=15, height=2)
        self.close_button.pack(side=tk.LEFT, padx=10)

        # クリップボードの監視設定
        self.clipboard_content = ''
        self.is_first_check = True
        self.check_clipboard()

        # テキスト変更イベントをバインド
        self.text_input.bind("<KeyRelease>", self.update_stats)

    def show_copy_notification(self):
        """コピー通知のポップアップウィンドウを表示"""
        popup = tk.Toplevel(self.root)
        popup.title("通知")
        popup.geometry("200x100")
        popup.geometry("+10+10")

        popup.configure(bg="#f0f0f0")
        popup.attributes("-topmost", True)

        label = tk.Label(popup, text="コピーしました", font=("Helvetica", 12), bg="#f0f0f0", pady=20)
        label.pack(expand=True, fill=tk.BOTH)

        popup.after(2000, popup.destroy)

    def check_clipboard(self):
        """クリップボードの内容を監視し、変更があれば取得して表示"""
        if self.is_monitoring_clipboard:
            try:
                clipboard_text = pyperclip.paste()
                if clipboard_text != self.clipboard_content:
                    self.clipboard_content = clipboard_text
                    if not self.is_first_check and clipboard_text:
                        current_text = self.text_input.get("1.0", tk.END).strip()
                        # 既存のテキストがある場合は改行を追加
                        if current_text:
                            self.text_input.insert(tk.END, "\n" + clipboard_text)
                        else:
                            self.text_input.insert(tk.END, clipboard_text)
                        self.update_stats(None)

                        # コピー通知のポップアップを表示
                        self.show_copy_notification()

                    self.is_first_check = False
            except Exception as e:
                print(f"クリップボード監視エラー: {e}")

        # 定期的に再チェック (500ミリ秒ごと)
        self.root.after(500, self.check_clipboard)

    def update_stats(self, event):
        """テキストの行数と文字数を更新"""
        text = self.text_input.get("1.0", tk.END)
        lines = text.count('\n')
        chars = len(text) - lines  # 改行文字を除く

        if text.strip() == "":
            lines = 0
            chars = 0

        self.stats_label.config(text=f"行数: {lines}  文字数: {chars}")

    def convert_to_json(self):
        """テキストをJSON形式に変換"""
        try:
            text = self.text_input.get("1.0", tk.END)
            if not text.strip():
                messagebox.showwarning("警告", "変換するテキストがありません。")
                return

            # クリップボード監視を停止
            self.stop_monitoring()

            # parse_medical_text関数を使用して変換
            parsed_data = parse_medical_text(text)

            # JSONに変換
            json_data = json.dumps(parsed_data, indent=2, ensure_ascii=False)

            # 出力エリアに表示
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, json_data)

            # クリップボードにJSONデータをコピー
            pyperclip.copy(json_data)

            # 完了メッセージを表示
            messagebox.showinfo("完了", "JSON形式に変換してコピーしました")

        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました: {e}")

    def clear_text(self):
        """入力テキストと出力テキストをクリア"""
        self.text_input.delete("1.0", tk.END)
        self.text_output.delete("1.0", tk.END)
        self.update_stats(None)

    def stop_monitoring(self):
        """クリップボード監視を停止"""
        self.is_monitoring_clipboard = False
        self.monitor_status_label.config(text="クリップボード監視: OFF", fg="red")

    def start_monitoring(self):
        """クリップボード監視を開始し、テキストをクリア"""
        self.is_monitoring_clipboard = True
        self.monitor_status_label.config(text="クリップボード監視: ON", fg="green")
        self.is_first_check = True
        # テキストをクリア
        self.text_input.delete("1.0", tk.END)
        self.text_output.delete("1.0", tk.END)
        self.update_stats(None)

    def run_mouse_automation(self):
        """mouse_automation.pyの機能を実行"""
        try:
            self.root.iconify()
            mouse_automation.main()
        except Exception as e:
            messagebox.showerror("エラー", f"マウス操作自動化の実行中にエラーが発生しました: {e}")

    def open_text_editor(self):
        """テキストエディタウィンドウを開く"""
        text_content = self.text_input.get("1.0", tk.END)
        editor = TextEditor(self.root, text_content)


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalTextConverter(root)
    root.mainloop()
