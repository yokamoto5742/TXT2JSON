import tempfile
import tkinter as tk
import os
from datetime import datetime
from tkinter import scrolledtext, messagebox
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

        self.on_close = None

        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("出力結果確認")
        self.window.geometry(f"{self.editor_width}x{self.editor_height}{self.editor_window_position}")
        self.window.minsize(self.editor_width, self.editor_height)

        self.text_area = scrolledtext.ScrolledText(self.window, wrap=tk.WORD,
                                                   font=(self.font_name, self.font_size))
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        if initial_text:
            self.text_area.insert(tk.END, initial_text)

        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        font_frame = tk.Frame(button_frame)
        font_frame.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(button_frame, text="テキストクリア", command=self.clear_text, width=15, height=2)
        clear_button.pack(side=tk.LEFT, padx=5)

        print_button = tk.Button(button_frame, text="印刷", command=self.print_text, width=15, height=2)
        print_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(button_frame, text="閉じる", command=self.close_window, width=15, height=2)
        close_button.pack(side=tk.LEFT, padx=5)

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def clear_text(self):
        if messagebox.askyesno("確認", "テキストをクリアしますか？"):
            self.text_area.delete(1.0, tk.END)

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
