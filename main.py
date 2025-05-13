import json

import pyperclip
import tkinter as tk
from tkinter import scrolledtext, messagebox

from services import mouse_automation
from services.txt_parse import parse_medical_text
from services.txt_editor import TextEditor
from utils.config_manager import load_config
from version import VERSION


class MedicalTextConverter:
    def __init__(self, root):
        self.root = root
        self.config = load_config()

        self.window_width = self.config.getint('Appearance', 'window_width', fallback=1200)
        self.window_height = self.config.getint('Appearance', 'window_height', fallback=800)
        self.main_window_position = self.config.get('Appearance', 'main_window_position', fallback='+10+10')
        self.text_area_font_size = self.config.getint('Appearance', 'text_area_font_size', fallback=11)
        self.text_area_font_name = self.config.get('Appearance', 'text_area_font_name', fallback='Yu Gothic UI')
        # ボタンサイズの設定を追加
        self.button_width = self.config.getint('Appearance', 'button_width', fallback=15)
        self.button_height = self.config.getint('Appearance', 'button_height', fallback=2)

        self.root.title(f"JSON形式変換 v{VERSION}")
        self.root.geometry(f"{self.window_width}x{self.window_height}{self.main_window_position}")

        self.is_monitoring_clipboard = False

        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill=tk.BOTH, expand=True)

        self.frame_karte = tk.LabelFrame(self.frame_top, text="カルテ記載")
        self.frame_karte.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_input = scrolledtext.ScrolledText(self.frame_karte, height=10,
                                                    font=(self.text_area_font_name, self.text_area_font_size))
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.frame_json = tk.LabelFrame(self.frame_top, text="JSON形式")
        self.frame_json.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_output = scrolledtext.ScrolledText(self.frame_json, height=10,
                                                     font=(self.text_area_font_name, self.text_area_font_size))
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 行数と文字数の表示
        self.frame_stats = tk.Frame(root)
        self.frame_stats.pack(fill=tk.X)

        self.stats_label = tk.Label(self.frame_stats, text="カルテ記載行数: 0  文字数: 0")
        self.stats_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.monitor_status_label = tk.Label(self.frame_stats, text="クリップボード監視: OFF", fg="red")
        self.monitor_status_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(fill=tk.X, pady=10)

        self.new_button = tk.Button(self.frame_buttons, text="新規登録",
                                    command=self.start_monitoring,
                                    width=self.button_width, height=self.button_height)
        self.new_button.pack(side=tk.LEFT, padx=10)

        self.soap_button = tk.Button(self.frame_buttons, text="詳細検索設定",
                                     command=self.run_mouse_automation,
                                     width=self.button_width, height=self.button_height)
        self.soap_button.pack(side=tk.LEFT, padx=10)

        self.soap_copy_button = tk.Button(self.frame_buttons, text="カルテコピー",
                                          command=self.soap_copy,
                                          width=self.button_width, height=self.button_height)
        self.soap_copy_button.pack(side=tk.LEFT, padx=10)

        self.convert_button = tk.Button(self.frame_buttons, text="JSON形式変換",
                                        command=self.convert_to_json,
                                        width=self.button_width, height=self.button_height)
        self.convert_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = tk.Button(self.frame_buttons, text="テキストクリア",
                                      command=self.clear_text,
                                      width=self.button_width, height=self.button_height)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        self.editor_button = tk.Button(self.frame_buttons, text="確認フォーム",
                                       command=self.open_text_editor,
                                       width=self.button_width, height=self.button_height)
        self.editor_button.pack(side=tk.LEFT, padx=10)

        self.close_button = tk.Button(self.frame_buttons, text="閉じる",
                                      command=self.root.destroy,
                                      width=self.button_width, height=self.button_height)
        self.close_button.pack(side=tk.LEFT, padx=10)

        self.clipboard_content = ''
        self.is_first_check = True
        self.check_clipboard()

        self.text_input.bind("<KeyRelease>", self.update_stats)

    def show_notification(self, message, timeout=2000, position=None):
        if position is None:
            position = self.main_window_position

        popup = tk.Toplevel(self.root)
        popup.title("通知")
        popup.geometry("200x100")
        popup.geometry(position)

        popup.configure(bg="#f0f0f0")
        popup.attributes("-topmost", True)

        label = tk.Label(popup, text=message, font=("MS Gothic", 12), bg="#f0f0f0", pady=20)
        label.pack(expand=True, fill=tk.BOTH)

        popup.after(timeout, popup.destroy)

    def check_clipboard(self):
        if self.is_monitoring_clipboard:
            try:
                clipboard_text = pyperclip.paste()
                if clipboard_text != self.clipboard_content:
                    self.clipboard_content = clipboard_text
                    if not self.is_first_check and clipboard_text:
                        current_text = self.text_input.get("1.0", tk.END).strip()
                        if current_text:
                            self.text_input.insert(tk.END, "\n" + clipboard_text)
                        else:
                            self.text_input.insert(tk.END, clipboard_text)
                        self.update_stats(None)

                        self.show_notification("コピーしました")

                    self.is_first_check = False
            except Exception as e:
                print(f"クリップボード監視エラー: {e}")

        self.root.after(500, self.check_clipboard)

    def update_stats(self, event):
        text = self.text_input.get("1.0", tk.END)
        lines = text.count('\n')
        chars = len(text) - lines  # 改行文字を除く

        if text.strip() == "":
            lines = 0
            chars = 0

        self.stats_label.config(text=f"行数: {lines}  文字数: {chars}")

    def soap_copy(self):
        try:
            self.root.iconify()
            mouse_automation.main("soap_copy")
            self.root.deiconify()
        except Exception as e:
            messagebox.showerror("エラー", f"SOAPコピー中にエラーが発生しました: {e}")

    def convert_to_json(self):
        try:
            text = self.text_input.get("1.0", tk.END)
            if not text.strip():
                messagebox.showwarning("警告", "変換するテキストがありません。")
                return

            self.set_monitoring_state(False)

            parsed_data = parse_medical_text(text)
            json_data = json.dumps(parsed_data, indent=2, ensure_ascii=False)

            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, json_data)

            pyperclip.copy(json_data)

            messagebox.showinfo("完了", "JSON形式に変換しコピーしました")

        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました: {e}")

    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.text_output.delete("1.0", tk.END)
        self.update_stats(None)

    def set_monitoring_state(self, enabled):
        self.is_monitoring_clipboard = enabled
        if enabled:
            self.monitor_status_label.config(text="クリップボード監視: ON", fg="green")
        else:
            self.monitor_status_label.config(text="クリップボード監視: OFF", fg="red")

    def start_monitoring(self):
        self.set_monitoring_state(True)
        self.clear_text()
        pyperclip.copy("")
        self.clipboard_content = ""
        self.is_first_check = False

    def run_mouse_automation(self):
        try:
            self.root.iconify()
            mouse_automation.main()
            self.show_notification("設定完了", timeout=2000)
        except Exception as e:
            messagebox.showerror("エラー", f"マウス操作自動化の実行中にエラーが発生しました: {e}")

    def open_text_editor(self):
        self.set_monitoring_state(False)
        self.root.withdraw()
        editor = TextEditor(self.root, "")
        editor.on_close = self._restore_clipboard_monitoring

    def _restore_clipboard_monitoring(self):
        self.is_monitoring_clipboard = False


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalTextConverter(root)
    root.mainloop()
