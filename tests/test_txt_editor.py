import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from datetime import datetime


class TestTextEditor:
    """TextEditorクラスのテスト"""

    @patch('services.txt_editor.load_config')
    @patch('tkinter.Toplevel')
    @patch('tkinter.scrolledtext.ScrolledText')
    @patch('tkinter.Frame')
    @patch('tkinter.Label')
    @patch('tkinter.Button')
    def test_init_with_parent(self, mock_button, mock_label, mock_frame,
                              mock_scrolled_text, mock_toplevel, mock_config):
        """親ウィンドウありでの初期化テスト"""
        from services.txt_editor import TextEditor

        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.getint.side_effect = lambda section, key, fallback=None: {
            'editor_width': 800,
            'editor_height': 800,
            'text_area_font_size': 11,
            'button_width': 15,
            'button_height': 2
        }.get(key, fallback)
        mock_config_obj.get.side_effect = lambda section, key, fallback=None: {
            'editor_window_position': '+10+10',
            'text_area_font_name': 'Yu Gothic UI'
        }.get(key, fallback)
        mock_config.return_value = mock_config_obj

        mock_parent = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window
        mock_text_area = Mock()
        mock_text_area.get.return_value = "初期テキスト"  # 修正：Mock戻り値を設定
        mock_scrolled_text.return_value = mock_text_area

        # テスト実行
        editor = TextEditor(mock_parent, "初期テキスト")

        # 検証
        mock_toplevel.assert_called_once_with(mock_parent)
        mock_window.title.assert_called_with("確認画面")
        mock_window.geometry.assert_called_with("800x800+10+10")
        mock_text_area.insert.assert_called_with("end", "初期テキスト")  # 修正：tk.ENDの実際の値

    @patch('services.txt_editor.load_config')
    @patch('tkinter.Tk')
    @patch('tkinter.scrolledtext.ScrolledText')
    @patch('tkinter.Frame')
    @patch('tkinter.Label')
    @patch('tkinter.Button')
    def test_init_without_parent(self, mock_button, mock_label, mock_frame,
                                 mock_scrolled_text, mock_tk, mock_config):
        """親ウィンドウなしでの初期化テスト"""
        from services.txt_editor import TextEditor

        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.getint.side_effect = lambda section, key, fallback=None: fallback
        mock_config_obj.get.side_effect = lambda section, key, fallback=None: fallback
        mock_config.return_value = mock_config_obj

        mock_window = Mock()
        mock_tk.return_value = mock_window
        mock_text_area = Mock()
        mock_text_area.get.return_value = ""  # 修正：Mock戻り値を設定
        mock_scrolled_text.return_value = mock_text_area

        # テスト実行
        editor = TextEditor(None, "")

        # 検証
        mock_tk.assert_called_once()
        mock_window.title.assert_called_with("確認画面")

    def create_mock_editor(self):
        """テスト用のモックエディタを作成"""
        with patch('services.txt_editor.load_config') as mock_config, \
                patch('tkinter.Toplevel') as mock_toplevel, \
                patch('tkinter.scrolledtext.ScrolledText') as mock_scrolled_text, \
                patch('tkinter.Frame'), \
                patch('tkinter.Label') as mock_label, \
                patch('tkinter.Button'):
            from services.txt_editor import TextEditor

            # モック設定
            mock_config_obj = Mock()
            mock_config_obj.getint.return_value = 11
            mock_config_obj.get.return_value = 'Yu Gothic UI'
            mock_config.return_value = mock_config_obj

            mock_text_area = Mock()
            mock_text_area.get.return_value = ""  # 修正：初期値を空文字列に設定
            mock_scrolled_text.return_value = mock_text_area
            mock_stats_label = Mock()
            mock_label.return_value = mock_stats_label
            mock_window = Mock()
            mock_toplevel.return_value = mock_window

            editor = TextEditor(Mock(), "")
            editor.text_area = mock_text_area
            editor.stats_label = mock_stats_label

            return editor, mock_text_area, mock_stats_label

    def test_update_stats_with_content(self):
        """コンテンツありでの統計更新テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # テキストの内容を設定
        mock_text_area.get.return_value = "行1\n行2\n行3\n"

        # テスト実行
        editor.update_stats(None)

        # 検証
        mock_stats_label.config.assert_called_with(text="行数: 3  文字数: 6")

    def test_update_stats_empty_content(self):
        """空コンテンツでの統計更新テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 空のテキストを設定
        mock_text_area.get.return_value = "   \n\n  \n"

        # テスト実行
        editor.update_stats(None)

        # 検証
        mock_stats_label.config.assert_called_with(text="行数: 0  文字数: 0")

    def test_update_stats_single_line(self):
        """単一行での統計更新テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 単一行のテキストを設定
        mock_text_area.get.return_value = "これは1行のテキストです"

        # テスト実行
        editor.update_stats(None)

        # 検証
        mock_stats_label.config.assert_called_with(text="行数: 0  文字数: 12")

    @patch('pyperclip.paste')
    @patch('tkinter.messagebox.showinfo')
    def test_paste_text_success(self, mock_showinfo, mock_paste):
        """テキスト貼り付け成功のテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # クリップボードの内容を設定
        mock_paste.return_value = "貼り付けテキスト"

        # テスト実行
        editor.paste_text()

        # 検証
        mock_text_area.insert.assert_called_with("insert", "貼り付けテキスト")  # 修正：tk.INSERTの実際の値

    @patch('pyperclip.paste')
    @patch('tkinter.messagebox.showinfo')
    def test_paste_text_empty_clipboard(self, mock_showinfo, mock_paste):
        """空クリップボードでの貼り付けテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 空のクリップボードを設定
        mock_paste.return_value = ""

        # テスト実行
        editor.paste_text()

        # 検証
        mock_showinfo.assert_called_with("情報", "クリップボードにテキストがありません。")
        mock_text_area.insert.assert_not_called()

    @patch('pyperclip.paste')
    @patch('tkinter.messagebox.showerror')
    def test_paste_text_error(self, mock_showerror, mock_paste):
        """貼り付けエラーのテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 例外を発生させる
        mock_paste.side_effect = Exception("クリップボードエラー")

        # テスト実行
        editor.paste_text()

        # 検証
        mock_showerror.assert_called()
        args = mock_showerror.call_args[0]
        assert args[0] == "エラー"
        assert "貼り付け中にエラーが発生しました" in args[1]

    @patch('tkinter.messagebox.askyesno')
    def test_clear_text_confirm_yes(self, mock_askyesno):
        """テキストクリア確認「はい」のテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 確認ダイアログで「はい」を選択
        mock_askyesno.return_value = True

        # テスト実行
        editor.clear_text()

        # 検証
        mock_askyesno.assert_called_with("確認", "テキストをクリアしますか？")
        mock_text_area.delete.assert_called_with(1.0, "end")  # 修正：tk.ENDの実際の値

    @patch('tkinter.messagebox.askyesno')
    def test_clear_text_confirm_no(self, mock_askyesno):
        """テキストクリア確認「いいえ」のテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 確認ダイアログで「いいえ」を選択
        mock_askyesno.return_value = False

        # テスト実行
        editor.clear_text()

        # 検証
        mock_askyesno.assert_called_with("確認", "テキストをクリアしますか？")
        mock_text_area.delete.assert_not_called()

    @patch('tempfile.gettempdir')
    @patch('os.system')
    @patch('tkinter.messagebox.showinfo')
    @patch('builtins.open', new_callable=mock_open)
    @patch('services.txt_editor.datetime')
    def test_print_text_success(self, mock_datetime, mock_file, mock_showinfo,
                                mock_system, mock_tempdir):
        """印刷成功のテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # モック設定
        mock_text_area.get.return_value = "印刷するテキスト"
        mock_tempdir.return_value = r"C:\temp"
        mock_datetime.now.return_value.strftime.return_value = "20240526_143000"

        # テスト実行
        editor.print_text()

        # 検証
        mock_file.assert_called_once()
        mock_system.assert_called_once()
        system_call = mock_system.call_args[0][0]
        assert 'notepad /p' in system_call
        assert 'print_20240526_143000.txt' in system_call

    @patch('tkinter.messagebox.showinfo')
    def test_print_text_empty_content(self, mock_showinfo):
        """空コンテンツでの印刷テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 空のテキストを設定
        mock_text_area.get.return_value = "   "

        # テスト実行
        editor.print_text()

        # 検証
        mock_showinfo.assert_called_with("情報", "印刷するテキストがありません。")

    @patch('tempfile.gettempdir')
    @patch('tkinter.messagebox.showerror')
    @patch('builtins.open', side_effect=Exception("ファイルエラー"))
    def test_print_text_error(self, mock_file, mock_showerror, mock_tempdir):
        """印刷エラーのテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # テキストを設定
        mock_text_area.get.return_value = "印刷するテキスト"
        mock_tempdir.return_value = r"C:\temp"

        # テスト実行
        editor.print_text()

        # 検証
        mock_showerror.assert_called()
        args = mock_showerror.call_args[0]
        assert args[0] == "エラー"
        assert "印刷中にエラーが発生しました" in args[1]

    def test_close_window_with_parent(self):
        """親ウィンドウありでのウィンドウクローズテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 親ウィンドウを設定
        mock_parent = Mock()
        mock_window = Mock()
        editor.parent = mock_parent
        editor.window = mock_window
        editor.on_close = Mock()

        # テスト実行
        editor.close_window()

        # 検証
        mock_window.destroy.assert_called_once()
        mock_parent.deiconify.assert_called_once()
        editor.on_close.assert_called_once()

    def test_close_window_without_parent(self):
        """親ウィンドウなしでのウィンドウクローズテスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 親ウィンドウなしを設定
        mock_window = Mock()
        editor.parent = None
        editor.window = mock_window

        # テスト実行
        editor.close_window()

        # 検証
        mock_window.quit.assert_called_once()

    def test_run_without_parent(self):
        """親ウィンドウなしでのrun実行テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 親ウィンドウなしを設定
        mock_window = Mock()
        editor.parent = None
        editor.window = mock_window

        # テスト実行
        editor.run()

        # 検証
        mock_window.mainloop.assert_called_once()

    def test_run_with_parent(self):
        """親ウィンドウありでのrun実行テスト"""
        editor, mock_text_area, mock_stats_label = self.create_mock_editor()

        # 親ウィンドウありを設定
        mock_parent = Mock()
        mock_window = Mock()
        editor.parent = mock_parent
        editor.window = mock_window

        # テスト実行
        editor.run()

        # 検証 - 親ウィンドウがある場合はmainloopは呼ばれない
        mock_window.mainloop.assert_not_called()


class TestTextEditorIntegration:
    """TextEditor統合テスト"""

    @patch('services.txt_editor.load_config')
    @patch('tkinter.Toplevel')
    @patch('tkinter.scrolledtext.ScrolledText')
    @patch('tkinter.Frame')
    @patch('tkinter.Label')
    @patch('tkinter.Button')
    @patch('pyperclip.paste')
    def test_full_workflow_paste_and_stats(self, mock_paste, mock_button, mock_label,
                                           mock_frame, mock_scrolled_text, mock_toplevel, mock_config):
        """貼り付けと統計更新の完全ワークフローテスト"""
        from services.txt_editor import TextEditor

        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.getint.return_value = 11
        mock_config_obj.get.return_value = 'Yu Gothic UI'
        mock_config.return_value = mock_config_obj

        mock_parent = Mock()
        mock_window = Mock()
        mock_toplevel.return_value = mock_window
        mock_text_area = Mock()
        mock_text_area.get.return_value = ""  # 修正：初期値を設定
        mock_scrolled_text.return_value = mock_text_area
        mock_stats_label = Mock()
        mock_label.return_value = mock_stats_label

        mock_paste.return_value = "テスト行1\nテスト行2\n"

        # テスト実行
        editor = TextEditor(mock_parent, "")
        editor.text_area = mock_text_area
        editor.stats_label = mock_stats_label

        # 貼り付け実行後にgetの戻り値を変更
        mock_text_area.get.return_value = "テスト行1\nテスト行2\n"

        editor.paste_text()
        editor.update_stats(None)

        # 検証
        mock_text_area.insert.assert_called_with("insert", "テスト行1\nテスト行2\n")  # 修正：tk.INSERTの実際の値
        mock_stats_label.config.assert_called_with(text="行数: 2  文字数: 10")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])