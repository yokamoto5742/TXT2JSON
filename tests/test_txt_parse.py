import pytest
from datetime import datetime
from services.txt_parse import (
    convert_to_timestamp,
    process_record,
    group_records_by_datetime,
    remove_duplicates,
    parse_medical_text
)


class TestConvertToTimestamp:
    """タイムスタンプ変換機能のテスト"""
    
    def test_valid_datetime_conversion(self):
        """正常な日付・時刻の変換テスト"""
        result = convert_to_timestamp("2024/05/26", "14:30")
        assert result == "2024-05-26T14:30:00Z"
        
    def test_edge_case_times(self):
        """境界値時刻のテスト"""
        assert convert_to_timestamp("2024/01/01", "00:00") == "2024-01-01T00:00:00Z"
        assert convert_to_timestamp("2024/12/31", "23:59") == "2024-12-31T23:59:00Z"
        
    def test_invalid_date_format(self):
        """無効な日付フォーマットのテスト"""
        assert convert_to_timestamp("2024-05-26", "14:30") is None
        assert convert_to_timestamp("24/05/26", "14:30") is None
        assert convert_to_timestamp("invalid", "14:30") is None
        
    def test_invalid_time_format(self):
        """無効な時刻フォーマットのテスト"""
        assert convert_to_timestamp("2024/05/26", "14-30") is None
        assert convert_to_timestamp("2024/05/26", "2:30") is None
        assert convert_to_timestamp("2024/05/26", "invalid") is None
        
    def test_none_inputs(self):
        """None入力のテスト"""
        assert convert_to_timestamp(None, "14:30") is None
        assert convert_to_timestamp("2024/05/26", None) is None


class TestProcessRecord:
    """レコード処理機能のテスト"""
    
    def test_process_valid_record(self):
        """有効なレコードの処理テスト"""
        current_record = {
            'date': '2024/05/26(日)',
            'department': '内科',
            'time': '14:30',
            'soap_section': 'S'
        }
        content_buffer = "患者の主訴"
        records = []
        
        result = process_record(current_record, content_buffer, records)
        
        assert len(records) == 1
        assert records[0]['content'] == "患者の主訴"
        assert result == ""
        
    def test_process_incomplete_record(self):
        """不完全なレコードの処理テスト"""
        current_record = {'date': '2024/05/26(日)'}  # soap_sectionなし
        content_buffer = "テスト内容"
        records = []
        
        result = process_record(current_record, content_buffer, records)
        
        assert len(records) == 0
        assert result == ""
        
    def test_process_empty_content(self):
        """空コンテンツの処理テスト"""
        current_record = {
            'date': '2024/05/26(日)',
            'department': '内科',
            'time': '14:30',
            'soap_section': 'S'
        }
        content_buffer = "   "  # 空白のみ
        records = []
        
        result = process_record(current_record, content_buffer, records)
        
        assert len(records) == 0


class TestGroupRecordsByDatetime:
    """日時によるレコードグループ化のテスト"""
    
    def test_group_single_record(self):
        """単一レコードのグループ化テスト"""
        records = [{
            'date': '2024/05/26(日)',
            'department': '内科',
            'time': '14:30',
            'soap_section': 'S',
            'content': '頭痛'
        }]
        
        result = group_records_by_datetime(records)
        
        assert len(result) == 1
        assert result[0]['subject'] == '頭痛'
        assert result[0]['timestamp'] == '2024-05-26T14:30:00Z'
        assert result[0]['department'] == '内科'
        
    def test_group_multiple_soap_sections(self):
        """複数SOAPセクションのグループ化テスト"""
        records = [
            {
                'date': '2024/05/26(日)',
                'department': '内科',
                'time': '14:30',
                'soap_section': 'S',
                'content': '頭痛'
            },
            {
                'date': '2024/05/26(日)',
                'department': '内科',
                'time': '14:30',
                'soap_section': 'O',
                'content': '血圧130/80'
            }
        ]
        
        result = group_records_by_datetime(records)
        
        assert len(result) == 1
        assert result[0]['subject'] == '頭痛'
        assert result[0]['object'] == '血圧130/80'
        
    def test_group_different_timestamps(self):
        """異なるタイムスタンプのグループ化テスト"""
        records = [
            {
                'date': '2024/05/26(日)',
                'department': '内科',
                'time': '14:30',
                'soap_section': 'S',
                'content': '頭痛'
            },
            {
                'date': '2024/05/26(日)',
                'department': '内科',
                'time': '15:30',
                'soap_section': 'S',
                'content': '発熱'
            }
        ]
        
        result = group_records_by_datetime(records)
        
        assert len(result) == 2
        
    def test_soap_section_mapping(self):
        """SOAPセクションマッピングのテスト"""
        records = [
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'S', 'content': 'S内容'},
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'O', 'content': 'O内容'},
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'A', 'content': 'A内容'},
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'P', 'content': 'P内容'},
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'F', 'content': 'F内容'},
            {'date': '2024/05/26(日)', 'department': '内科', 'time': '14:30', 'soap_section': 'サ', 'content': 'サ内容'}
        ]
        
        result = group_records_by_datetime(records)
        
        assert len(result) == 1
        record = result[0]
        assert record['subject'] == 'S内容'
        assert record['object'] == 'O内容'
        assert record['assessment'] == 'A内容'
        assert record['plan'] == 'P内容'
        assert record['comment'] == 'F内容'
        assert record['summary'] == 'サ内容'


class TestRemoveDuplicates:
    """重複除去機能のテスト"""
    
    def test_remove_exact_duplicates(self):
        """完全重複レコードの除去テスト"""
        records = [
            {'timestamp': '2024-05-26T14:30:00Z', 'subject': '頭痛'},
            {'timestamp': '2024-05-26T14:30:00Z', 'subject': '頭痛'},
            {'timestamp': '2024-05-26T15:30:00Z', 'subject': '発熱'}
        ]
        
        result = remove_duplicates(records)
        
        assert len(result) == 2
        
    def test_no_duplicates(self):
        """重複なしレコードのテスト"""
        records = [
            {'timestamp': '2024-05-26T14:30:00Z', 'subject': '頭痛'},
            {'timestamp': '2024-05-26T15:30:00Z', 'subject': '発熱'}
        ]
        
        result = remove_duplicates(records)
        
        assert len(result) == 2
        
    def test_empty_list(self):
        """空リストのテスト"""
        result = remove_duplicates([])
        assert len(result) == 0


class TestParseMedicalText:
    """医療テキスト解析のテスト"""
    
    def test_parse_simple_text(self):
        """シンプルなテキストの解析テスト"""
        text = """2024/05/26(日)
内科    担当医    外来    14:30
S >
頭痛があります
O >
血圧 130/80
体温 36.5℃
"""
        
        result = parse_medical_text(text)
        
        assert len(result) == 1
        record = result[0]
        assert record['timestamp'] == '2024-05-26T14:30:00Z'
        assert record['department'] == '内科'
        assert '頭痛があります' in record['subject']
        assert '血圧 130/80' in record['object']
        
    def test_parse_multiple_entries(self):
        """複数エントリのテキスト解析テスト"""
        text = """2024/05/26(日)
内科    担当医    外来    14:30
S >
頭痛があります

2024/05/26(日)
外科    担当医    外来    15:30
S >
腹痛があります
"""
        
        result = parse_medical_text(text)
        
        assert len(result) == 2
        
    def test_parse_empty_text(self):
        """空テキストの解析テスト"""
        result = parse_medical_text("")
        assert len(result) == 0
        
    def test_parse_malformed_text(self):
        """不正形式テキストの解析テスト"""
        text = """これは不正な形式のテキストです
日付がありません
SOAPセクションもありません
"""
        
        result = parse_medical_text(text)
        assert len(result) == 0
        
    def test_parse_with_hospitalization_day(self):
        """入院日数付きテキストの解析テスト"""
        text = """2024/05/26(日) （入院 5 日目）
内科    担当医    病棟    09:00
S >
体調は良好です
"""
        
        result = parse_medical_text(text)
        
        assert len(result) == 1
        # 入院日数は日付パースで処理されるが、現在の実装では特別な処理はなし


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
