import tempfile
import tkinter as tk
import os
from datetime import datetime
from tkinter import scrolledtext, messagebox

import pyperclip

from utils.config_manager import load_config


class TextEditor:
    def __init__(self, parent=None, initial_text=""):
        self.parent = parent
        self.config = load_config()

        self.editor_width = self.config.getint('Appearance', 'editor_width', fallback=600)
        self.editor_height = self.config.getint('Appearance', 'editor_height', fallback=600)
        self.editor_window_position = self.config.get('Appearance', 'editor_window_position', fallback='+10+10')
        self.font_size = self.config.getint('Appearance', 'text_area_font_size', fallback=11)
        self.font_name = self.config.get('Appearance', 'text_area_font_name', fallback='Yu Gothic UI')
        self.button_width = self.config.getint('Appearance', 'button_width', fallback=15)
        self.button_height = self.config.getint('Appearance', 'button_height', fallback=2)

        self.on_close = None

        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("確認フォーム")
        self.window.geometry(f"{self.editor_width}x{self.editor_height}{self.editor_window_position}")
        self.window.minsize(self.editor_width, self.editor_height)

        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                   font=(self.font_name, self.font_size))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        if initial_text:
            self.text_area.insert(tk.END, initial_text)

        stats_frame = tk.Frame(self.window)
        stats_frame.pack(fill=tk.X, padx=10)

        self.stats_label = tk.Label(stats_frame, text="行数: 0  文字数: 0")
        self.stats_label.pack(side=tk.LEFT, padx=5, pady=5)

        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        font_frame = tk.Frame(button_frame)
        font_frame.pack(side=tk.LEFT, padx=5)

        paste_button = tk.Button(button_frame, text="貼り付け", command=self.paste_text,
                                 width=self.button_width, height=self.button_height)
        paste_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(button_frame, text="クリア", command=self.clear_text,
                                 width=self.button_width, height=self.button_height)
        clear_button.pack(side=tk.LEFT, padx=5)

        print_button = tk.Button(button_frame, text="印刷", command=self.print_text,
                                 width=self.button_width, height=self.button_height)
        print_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(button_frame, text="閉じる", command=self.close_window,
                                 width=self.button_width, height=self.button_height)
        close_button.pack(side=tk.LEFT, padx=5)

        self.text_area.bind("<KeyRelease>", self.update_stats)
        self.update_stats(None)

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def update_stats(self, event):
        text = self.text_area.get("1.0", tk.END)
        lines = text.count('\n')
        chars = len(text) - lines  # 改行文字を除く

        if text.strip() == "":
            lines = 0
            chars = 0

        self.stats_label.config(text=f"行数: {lines}  文字数: {chars}")

    def paste_text(self):
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.text_area.insert(tk.INSERT, clipboard_text)
                self.update_stats(None)
            else:
                messagebox.showinfo("情報", "クリップボードにテキストがありません。")
        except Exception as e:
            messagebox.showerror("エラー", f"貼り付け中にエラーが発生しました: {e}")

    def clear_text(self):
        if messagebox.askyesno("確認", "テキストをクリアしますか？"):
            self.text_area.delete(1.0, tk.END)
            self.update_stats(None)

    def print_text(self):
        try:
            text_content = self.text_area.get(1.0, tk.END)
            if not text_content.strip():
                messagebox.showinfo("情報", "印刷するテキストがありません。")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"print_{timestamp}.txt"

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, file_name)

            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(text_content)

            os.system(f'notepad /p "{temp_file}"')

        except Exception as e:
            messagebox.showerror("エラー", f"印刷中にエラーが発生しました: {e}")

    def close_window(self):
        if self.parent:
            self.window.destroy()
            self.parent.deiconify()
            if self.on_close:
                self.on_close()
        else:
            self.window.quit()

    def run(self):
        if not self.parent:
            self.window.mainloop()


if __name__ == "__main__":
    editor = TextEditor()
    editor.run()
