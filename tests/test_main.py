import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tkinter as tk


class TestMedicalTextConverter:
    """MedicalTextConverterクラスのテスト"""

    def create_mock_converter(self):
        """テスト用のモックコンバーターを作成"""
        with patch('main.load_config') as mock_load_config, \
                patch('tkinter.Frame') as mock_frame, \
                patch('tkinter.LabelFrame') as mock_labelframe, \
                patch('tkinter.scrolledtext.ScrolledText') as mock_scrolled_text, \
                patch('tkinter.Label') as mock_label, \
                patch('tkinter.Button') as mock_button, \
                patch('pyperclip.copy') as mock_copy, \
                patch('main.parse_medical_text') as mock_parse, \
                patch('main.TextEditor') as mock_text_editor:
            from main import MedicalTextConverter

            # 設定モック
            mock_config = Mock()
            mock_config.getint.side_effect = lambda section, key, fallback=None: {
                'window_width': 1100,
                'window_height': 800,
                'text_area_font_size': 11,
                'button_width': 15,
                'button_height': 2
            }.get(key, fallback)
            mock_config.get.side_effect = lambda section, key, fallback=None: {
                'main_window_position': '+10+10',
                'text_area_font_name': 'Yu Gothic UI'
            }.get(key, fallback)
            mock_load_config.return_value = mock_config

            # tkinter要素のモック
            mock_root = Mock()
            mock_text_input = Mock()
            mock_text_output = Mock()
            mock_stats_label = Mock()
            mock_monitor_status_label = Mock()

            mock_text_input.get.return_value = "\n"
            mock_scrolled_text.side_effect = [mock_text_input, mock_text_output]
            mock_label.side_effect = [mock_stats_label, mock_monitor_status_label]

            # インスタンス作成
            converter = MedicalTextConverter(mock_root)

            # モックオブジェクトを設定
            converter.text_input = mock_text_input
            converter.text_output = mock_text_output
            converter.stats_label = mock_stats_label
            converter.monitor_status_label = mock_monitor_status_label

            return converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor

    def test_init_configuration_loading(self):
        """初期化時の設定読み込みテスト"""
        with patch('main.load_config') as mock_load_config, \
                patch('tkinter.Frame'), \
                patch('tkinter.LabelFrame'), \
                patch('tkinter.scrolledtext.ScrolledText'), \
                patch('tkinter.Label'), \
                patch('tkinter.Button'), \
                patch('main.parse_medical_text'), \
                patch('main.TextEditor'):
            from main import MedicalTextConverter

            mock_config = Mock()
            mock_config.getint.return_value = 1100
            mock_config.get.return_value = '+10+10'
            mock_load_config.return_value = mock_config

            mock_root = Mock()
            converter = MedicalTextConverter(mock_root)

            # 検証
            mock_load_config.assert_called_once()
            mock_root.title.assert_called()
            mock_root.geometry.assert_called()

    def test_update_stats_with_content(self):
        """コンテンツありでの統計更新テスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テキスト入力のモック設定
        mock_text_input.get.return_value = "行1\n行2\n行3\n"

        # テスト実行
        converter.update_stats(None)

        # 検証
        mock_stats_label.config.assert_called_with(text="行数: 3  文字数: 6")

    def test_update_stats_empty_content(self):
        """空コンテンツでの統計更新テスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 空のテキスト入力
        mock_text_input.get.return_value = "   \n  \n  "

        # テスト実行
        converter.update_stats(None)

        # 検証
        mock_stats_label.config.assert_called_with(text="行数: 0  文字数: 0")

    def test_set_monitoring_state_enabled(self):
        """クリップボード監視有効化のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト実行
        converter.set_monitoring_state(True)

        # 検証
        assert converter.is_monitoring_clipboard is True
        mock_monitor_status_label.config.assert_called_with(text="クリップボード監視: ON", fg="green")

    def test_set_monitoring_state_disabled(self):
        """クリップボード監視無効化のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト実行
        converter.set_monitoring_state(False)

        # 検証
        assert converter.is_monitoring_clipboard is False
        mock_monitor_status_label.config.assert_called_with(text="クリップボード監視: OFF", fg="red")

    @patch('pyperclip.copy')
    def test_start_monitoring(self, mock_copy_patch):
        """監視開始のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト実行
        converter.start_monitoring()

        # 検証
        assert converter.is_monitoring_clipboard is True
        mock_text_input.delete.assert_called_with("1.0", "end")
        mock_text_output.delete.assert_called_with("1.0", "end")
        mock_copy_patch.assert_called_with("")
        assert converter.clipboard_content == ""
        assert converter.is_first_check is False

    def test_clear_text(self):
        """テキストクリアのテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト実行
        converter.clear_text()

        # 検証
        mock_text_input.delete.assert_called_with("1.0", "end")
        mock_text_output.delete.assert_called_with("1.0", "end")

    @patch('pyperclip.paste')
    def test_check_clipboard_new_content(self, mock_paste):
        """新しいクリップボードコンテンツの検出テスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 初期設定
        converter.is_monitoring_clipboard = True
        converter.is_first_check = False
        converter.clipboard_content = "古いコンテンツ"
        mock_paste.return_value = "新しいコンテンツ"
        mock_text_input.get.return_value = "既存のテキスト"

        # show_notificationメソッドをモック
        converter.show_notification = Mock()

        # テスト実行
        converter.check_clipboard()

        # 検証
        assert converter.clipboard_content == "新しいコンテンツ"
        mock_text_input.insert.assert_called()
        converter.show_notification.assert_called_with("コピーしました")

    @patch('pyperclip.paste')
    def test_check_clipboard_monitoring_disabled(self, mock_paste):
        """監視無効時のクリップボードチェックテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 監視を無効化
        converter.is_monitoring_clipboard = False
        mock_paste.return_value = "新しいコンテンツ"

        # テスト実行
        converter.check_clipboard()

        # 検証 - 監視が無効なので何も処理されない
        mock_text_input.insert.assert_not_called()

    @patch('pyperclip.paste')
    def test_check_clipboard_first_check(self, mock_paste):
        """初回チェック時のクリップボード処理テスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 初回チェック設定
        converter.is_monitoring_clipboard = True
        converter.is_first_check = True
        converter.clipboard_content = ""
        mock_paste.return_value = "初回コンテンツ"

        # テスト実行
        converter.check_clipboard()

        # 検証 - 初回チェックなのでテキスト挿入はされない
        assert converter.clipboard_content == "初回コンテンツ"
        assert converter.is_first_check is False
        mock_text_input.insert.assert_not_called()

    @patch('pyperclip.paste')
    def test_check_clipboard_exception_handling(self, mock_paste):
        """クリップボードチェック例外処理のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 例外を発生させる
        converter.is_monitoring_clipboard = True
        mock_paste.side_effect = Exception("クリップボードエラー")

        # printをモック
        with patch('builtins.print') as mock_print:
            # テスト実行
            converter.check_clipboard()

            # 検証
            mock_print.assert_called()
            print_args = mock_print.call_args[0][0]
            assert "クリップボード監視エラー" in print_args

    @patch('services.mouse_automation.main')
    @patch('tkinter.messagebox.showerror')
    def test_soap_copy_success(self, mock_showerror, mock_mouse_main):
        """SOAPコピー成功のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト実行
        converter.soap_copy()

        # 検証
        converter.root.iconify.assert_called_once()
        mock_mouse_main.assert_called_with("soap_copy")
        converter.root.deiconify.assert_called_once()

    @patch('services.mouse_automation.main')
    @patch('tkinter.messagebox.showerror')
    def test_soap_copy_error(self, mock_showerror, mock_mouse_main):
        """SOAPコピーエラーのテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 例外を発生させる
        mock_mouse_main.side_effect = Exception("SOAPエラー")

        # テスト実行
        converter.soap_copy()

        # 検証
        mock_showerror.assert_called()
        args = mock_showerror.call_args[0]
        assert args[0] == "エラー"
        assert "SOAPコピー中にエラーが発生しました" in args[1]

    @patch('pyperclip.copy')
    @patch('main.parse_medical_text')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showwarning')
    def test_convert_to_json_success(self, mock_showwarning, mock_showinfo, mock_parse_method, mock_copy_method):
        """JSON変換成功のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # テスト入力データ（get()は末尾に改行を含む）
        mock_text_input.get.return_value = "医療テキスト\n"
        mock_parse_method.return_value = [{"date": "2024/05/26", "content": "テストデータ"}]

        # テスト実行
        converter.convert_to_json()

        # 検証（get()の戻り値をそのまま渡すので、改行付きで呼ばれる）
        mock_parse_method.assert_called_with("医療テキスト\n")
        mock_text_output.delete.assert_called_with("1.0", "end")
        mock_text_output.insert.assert_called()
        mock_copy_method.assert_called()
        mock_showinfo.assert_called_with("完了", "JSON形式に変換しコピーしました")
        assert converter.is_monitoring_clipboard is False

    @patch('tkinter.messagebox.showwarning')
    def test_convert_to_json_empty_text(self, mock_showwarning):
        """空テキストでのJSON変換テスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 空のテキスト入力
        mock_text_input.get.return_value = "   "

        # テスト実行
        converter.convert_to_json()

        # 検証
        mock_showwarning.assert_called_with("警告", "変換するテキストがありません。")

    @patch('main.parse_medical_text')
    @patch('tkinter.messagebox.showerror')
    def test_convert_to_json_error(self, mock_showerror, mock_parse_method):
        """JSON変換エラーのテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # エラーを発生させる
        mock_text_input.get.return_value = "医療テキスト\n"
        mock_parse_method.side_effect = Exception("パースエラー")

        # テスト実行
        converter.convert_to_json()

        # 検証
        mock_showerror.assert_called()
        args = mock_showerror.call_args[0]
        assert args[0] == "エラー"
        assert "変換中にエラーが発生しました" in args[1]

    @patch('services.mouse_automation.main')
    @patch('tkinter.messagebox.showerror')
    def test_run_mouse_automation_success(self, mock_showerror, mock_mouse_main):
        """マウス自動化実行成功のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # show_notificationメソッドをモック
        converter.show_notification = Mock()

        # テスト実行
        converter.run_mouse_automation()

        # 検証
        converter.root.iconify.assert_called_once()
        mock_mouse_main.assert_called_with()
        converter.show_notification.assert_called_with("設定完了", timeout=2000)

    @patch('services.mouse_automation.main')
    @patch('tkinter.messagebox.showerror')
    def test_run_mouse_automation_error(self, mock_showerror, mock_mouse_main):
        """マウス自動化実行エラーのテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # エラーを発生させる
        mock_mouse_main.side_effect = Exception("マウス操作エラー")

        # テスト実行
        converter.run_mouse_automation()

        # 検証
        mock_showerror.assert_called()
        args = mock_showerror.call_args[0]
        assert args[0] == "エラー"
        assert "マウス操作中にエラーが発生しました" in args[1]

    @patch('main.TextEditor')
    def test_open_text_editor(self, mock_text_editor_method):
        """テキストエディタ開くテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # モックエディタインスタンス
        mock_editor_instance = Mock()
        mock_text_editor_method.return_value = mock_editor_instance

        # テスト実行
        converter.open_text_editor()

        # 検証
        assert converter.is_monitoring_clipboard is False
        converter.root.withdraw.assert_called_once()
        mock_text_editor_method.assert_called_with(converter.root, "")
        assert mock_editor_instance.on_close == converter._restore_clipboard_monitoring

    def test_restore_clipboard_monitoring(self):
        """クリップボード監視復元のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # 監視状態を設定
        converter.is_monitoring_clipboard = True

        # テスト実行
        converter._restore_clipboard_monitoring()

        # 検証
        assert converter.is_monitoring_clipboard is False

    def test_show_notification(self):
        """通知表示のテスト"""
        converter, mock_text_input, mock_text_output, mock_stats_label, mock_monitor_status_label, mock_copy, mock_parse, mock_text_editor = self.create_mock_converter()

        # Toplevelと関連要素をモック
        with patch('tkinter.Toplevel') as mock_toplevel, \
                patch('tkinter.Label') as mock_notification_label:
            mock_popup = Mock()
            mock_toplevel.return_value = mock_popup
            mock_label_instance = Mock()
            mock_notification_label.return_value = mock_label_instance

            # テスト実行
            converter.show_notification("テストメッセージ", timeout=1000, position="+100+100")

            # 検証
            mock_toplevel.assert_called_with(converter.root)
            mock_popup.title.assert_called_with("通知")
            geometry_calls = mock_popup.geometry.call_args_list
            assert geometry_calls[0] == (("200x100",),)
            assert geometry_calls[1] == (("+100+100",),)
            mock_popup.after.assert_called_with(1000, mock_popup.destroy)


class TestMedicalTextConverterIntegration:
    """MedicalTextConverter統合テスト"""

    @patch('main.load_config')
    @patch('tkinter.Frame')
    @patch('tkinter.LabelFrame')
    @patch('tkinter.scrolledtext.ScrolledText')
    @patch('tkinter.Label')
    @patch('tkinter.Button')
    @patch('main.parse_medical_text')
    @patch('pyperclip.copy')
    @patch('tkinter.messagebox.showinfo')
    @patch('main.TextEditor')
    def test_full_conversion_workflow(self, mock_text_editor, mock_showinfo, mock_copy, mock_parse_method,
                                      mock_button, mock_label, mock_scrolled_text,
                                      mock_labelframe, mock_frame, mock_load_config):
        """完全な変換ワークフローの統合テスト"""
        from main import MedicalTextConverter

        # 設定とモックの準備
        mock_config = Mock()
        mock_config.getint.return_value = 11
        mock_config.get.return_value = 'Yu Gothic UI'
        mock_load_config.return_value = mock_config

        mock_text_input = Mock()
        mock_text_output = Mock()
        mock_text_input.get.return_value = "2024/05/26(日)\n内科 医師 外来 14:30\nS >\n頭痛があります\n"

        mock_scrolled_text.side_effect = [mock_text_input, mock_text_output]
        mock_parse_method.return_value = [{"timestamp": "2024-05-26T14:30:00Z", "subject": "頭痛があります"}]

        # テスト実行
        mock_root = Mock()
        converter = MedicalTextConverter(mock_root)
        converter.text_input = mock_text_input
        converter.text_output = mock_text_output

        converter.convert_to_json()

        # 検証（get()の戻り値をそのまま渡す）
        mock_parse_method.assert_called_once_with("2024/05/26(日)\n内科 医師 外来 14:30\nS >\n頭痛があります\n")
        mock_text_output.delete.assert_called_with("1.0", "end")
        mock_text_output.insert.assert_called()
        mock_copy.assert_called()
        mock_showinfo.assert_called_with("完了", "JSON形式に変換しコピーしました")


class TestMainFunction:
    """main関数のテスト"""

    @patch('main.MedicalTextConverter')
    @patch('tkinter.Tk')
    @patch('main.parse_medical_text')
    @patch('main.TextEditor')
    def test_main_execution(self, mock_text_editor, mock_parse, mock_tk, mock_converter_class):
        """メイン実行のテスト"""
        from main import MedicalTextConverter

        # モック設定
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_converter_instance = Mock()
        mock_converter_class.return_value = mock_converter_instance

        # main部分を直接テスト
        # （実際のコードではif __name__ == "__main__":の部分）
        root = mock_tk()
        app = mock_converter_class(root)

        # 検証
        mock_tk.assert_called_once()
        mock_converter_class.assert_called_once_with(mock_root)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])