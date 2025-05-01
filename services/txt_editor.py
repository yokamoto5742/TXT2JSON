import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import tempfile
from datetime import datetime


class TextEditor:
    def __init__(self, parent=None, initial_text=""):
        self.parent = parent
        self.initial_text = initial_text
        self.font_size = 10  # デフォルトのフォントサイズ
        self.on_close = None  # 閉じる際のコールバック関数

        # 新しいウィンドウを作成
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("テキストエディタ")
        self.window.geometry("800x600")

        # メインのテキストエリア
        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, font=("Yu Gothic UI", self.font_size))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 初期テキストがあれば設定
        if initial_text:
            self.text_area.insert(tk.END, initial_text)

        # ボタンフレーム
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # フォントサイズ変更フレーム
        font_frame = tk.Frame(button_frame)
        font_frame.pack(side=tk.LEFT, padx=5)

        # フォントサイズラベル
        font_label = tk.Label(font_frame, text="文字サイズ:")
        font_label.pack(side=tk.LEFT)

        # フォントサイズ減少ボタン
        decrease_font = tk.Button(font_frame, text="-", command=self.decrease_font_size, width=2)
        decrease_font.pack(side=tk.LEFT)

        # フォントサイズ表示
        self.font_size_var = tk.StringVar()
        self.font_size_var.set(str(self.font_size))
        font_size_display = tk.Label(font_frame, textvariable=self.font_size_var, width=2)
        font_size_display.pack(side=tk.LEFT)

        # フォントサイズ増加ボタン
        increase_font = tk.Button(font_frame, text="+", command=self.increase_font_size, width=2)
        increase_font.pack(side=tk.LEFT)

        # テキストクリアボタン
        clear_button = tk.Button(button_frame, text="テキストクリア", command=self.clear_text, width=15, height=2)
        clear_button.pack(side=tk.LEFT, padx=5)

        # 印刷ボタン
        print_button = tk.Button(button_frame, text="印刷", command=self.print_text, width=15, height=2)
        print_button.pack(side=tk.LEFT, padx=5)

        # 閉じるボタン
        close_button = tk.Button(button_frame, text="閉じる", command=self.close_window, width=15, height=2)
        close_button.pack(side=tk.LEFT, padx=5)

        # ウィンドウが閉じられたとき
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def clear_text(self):
        """テキストエリアをクリア"""
        if messagebox.askyesno("確認", "テキストをクリアしますか？"):
            self.text_area.delete(1.0, tk.END)

    def print_text(self):
        """テキストを印刷する（A4サイズ）"""
        try:
            text_content = self.text_area.get(1.0, tk.END)
            if not text_content.strip():
                messagebox.showinfo("情報", "印刷するテキストがありません。")
                return

            # 印刷のためのファイル名（日時を含む）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"medical_text_{timestamp}.txt"

            # 一時ファイルに保存
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, file_name)

            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(text_content)

            # Windowsのメモ帳で印刷ダイアログを開く
            os.system(f'notepad /p "{temp_file}"')

            messagebox.showinfo("印刷", "印刷ダイアログを開きました。")

        except Exception as e:
            messagebox.showerror("エラー", f"印刷中にエラーが発生しました: {e}")

    def close_window(self):
        """ウィンドウを閉じる"""
        if self.parent:
            # メインウィンドウの子ウィンドウの場合
            self.window.destroy()
            # メインウィンドウを再表示
            self.parent.deiconify()
            # 閉じる際のコールバックがあれば実行（クリップボード監視の再開など）
            if self.on_close:
                self.on_close()
        else:
            # 単独で実行された場合
            self.window.quit()

    def get_text(self):
        """現在のテキストを取得"""
        return self.text_area.get(1.0, tk.END)

    def increase_font_size(self):
        """フォントサイズを増加"""
        if self.font_size < 36:  # 最大フォントサイズ
            self.font_size += 1
            self.update_font()

    def decrease_font_size(self):
        """フォントサイズを減少"""
        if self.font_size > 10:  # 最小フォントサイズ
            self.font_size -= 1
            self.update_font()

    def update_font(self):
        """フォントを更新"""
        self.text_area.configure(font=("Yu Gothic UI", self.font_size))
        self.font_size_var.set(str(self.font_size))

    def run(self):
        """ウィンドウを実行（単独で実行する場合）"""
        if not self.parent:
            self.window.mainloop()


# スタンドアロンで実行する場合
if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
