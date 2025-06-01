import pytest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import os
from services.mouse_automation import soap_copy, run_mouse_operation, main


class TestMouseAutomation:
    """マウス自動化機能のテスト"""
    
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_soap_copy_success(self, mock_subprocess, mock_exists, mock_config):
        """SOAPコピー成功のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\soap_copy.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.return_value = None
        
        # テスト実行
        soap_copy()
        
        # 検証
        mock_config_obj.get.assert_called_once_with('Paths', 'soap_copy_file_path')
        mock_exists.assert_called_once_with(r'C:\test\soap_copy.exe')
        mock_subprocess.assert_called_once_with([r'C:\test\soap_copy.exe'], check=True)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_soap_copy_file_not_found(self, mock_print, mock_exists, mock_config):
        """SOAPコピーファイル未発見のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\nonexistent.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = False
        
        # テスト実行
        soap_copy()
        
        # 検証
        mock_print.assert_called_with(f"エラー: ファイルが見つかりません: C:\\test\\nonexistent.exe")
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_soap_copy_subprocess_error(self, mock_print, mock_subprocess, mock_exists, mock_config):
        """SOAPコピーサブプロセスエラーのテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\soap_copy.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'test')
        
        # テスト実行
        soap_copy()
        
        # 検証
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("SOAPコピーEXE実行エラー" in call for call in print_calls)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_soap_copy_general_exception(self, mock_print, mock_subprocess, mock_exists, mock_config):
        """SOAPコピー一般例外のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\soap_copy.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.side_effect = Exception("テスト例外")
        
        # テスト実行
        soap_copy()
        
        # 検証
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("SOAPコピーエラー" in call for call in print_calls)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_run_mouse_operation_success(self, mock_subprocess, mock_exists, mock_config):
        """マウス操作成功のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\mouse_operation.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.return_value = None
        
        # テスト実行
        run_mouse_operation()
        
        # 検証
        mock_config_obj.get.assert_called_once_with('Paths', 'operation_file_path')
        mock_exists.assert_called_once_with(r'C:\test\mouse_operation.exe')
        mock_subprocess.assert_called_once_with([r'C:\test\mouse_operation.exe'], check=True)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_run_mouse_operation_file_not_found(self, mock_print, mock_exists, mock_config):
        """マウス操作ファイル未発見のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\nonexistent.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = False
        
        # テスト実行
        run_mouse_operation()
        
        # 検証
        mock_print.assert_called_with(f"エラー: ファイルが見つかりません: C:\\test\\nonexistent.exe")
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_run_mouse_operation_subprocess_error(self, mock_print, mock_subprocess, mock_exists, mock_config):
        """マウス操作サブプロセスエラーのテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\mouse_operation.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'test')
        
        # テスト実行
        run_mouse_operation()
        
        # 検証
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("マウス操作EXE実行エラー" in call for call in print_calls)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_run_mouse_operation_general_exception(self, mock_print, mock_subprocess, mock_exists, mock_config):
        """マウス操作一般例外のテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\mouse_operation.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.side_effect = Exception("テスト例外")
        
        # テスト実行
        run_mouse_operation()
        
        # 検証
        mock_print.assert_called()
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("マウス操作エラー" in call for call in print_calls)


class TestMain:
    """メイン関数のテスト"""
    
    @patch('services.mouse_automation.soap_copy')
    def test_main_soap_copy(self, mock_soap_copy):
        """メイン関数 - SOAPコピーのテスト"""
        main("soap_copy")
        mock_soap_copy.assert_called_once()
        
    @patch('services.mouse_automation.run_mouse_operation')
    def test_main_mouse_operation(self, mock_mouse_operation):
        """メイン関数 - マウス操作のテスト"""
        main()
        mock_mouse_operation.assert_called_once()
        
    @patch('services.mouse_automation.run_mouse_operation')
    def test_main_default_operation(self, mock_mouse_operation):
        """メイン関数 - デフォルト操作のテスト"""
        main("unknown_operation")
        mock_mouse_operation.assert_called_once()
        
    @patch('services.mouse_automation.run_mouse_operation')
    def test_main_none_operation(self, mock_mouse_operation):
        """メイン関数 - None操作のテスト"""
        main(None)
        mock_mouse_operation.assert_called_once()


# 設定ファイル関連のテスト用フィクスチャ
@pytest.fixture
def mock_config():
    """設定ファイルのモックフィクスチャ"""
    config = Mock()
    config.get.side_effect = lambda section, key: {
        ('Paths', 'soap_copy_file_path'): r'C:\test\soap_copy.exe',
        ('Paths', 'operation_file_path'): r'C:\test\mouse_operation.exe'
    }.get((section, key), 'default_value')
    return config


class TestIntegration:
    """統合テスト"""
    
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_full_workflow_soap_copy(self, mock_subprocess, mock_exists, mock_config, mock_config_fixture=None):
        """SOAPコピー完全ワークフローのテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\soap_copy.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.return_value = None
        
        # テスト実行
        main("soap_copy")
        
        # 検証
        mock_config.assert_called_once()
        mock_exists.assert_called_once_with(r'C:\test\soap_copy.exe')
        mock_subprocess.assert_called_once_with([r'C:\test\soap_copy.exe'], check=True)
        
    @patch('services.mouse_automation.load_config')
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_full_workflow_mouse_operation(self, mock_subprocess, mock_exists, mock_config):
        """マウス操作完全ワークフローのテスト"""
        # モック設定
        mock_config_obj = Mock()
        mock_config_obj.get.return_value = r'C:\test\mouse_operation.exe'
        mock_config.return_value = mock_config_obj
        mock_exists.return_value = True
        mock_subprocess.return_value = None
        
        # テスト実行
        main()
        
        # 検証
        mock_config.assert_called_once()
        mock_exists.assert_called_once_with(r'C:\test\mouse_operation.exe')
        mock_subprocess.assert_called_once_with([r'C:\test\mouse_operation.exe'], check=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
