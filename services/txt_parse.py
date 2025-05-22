import json
import os
import re
from io import StringIO
from collections import defaultdict


def process_record(current_record, content_buffer, records, new_record_data=None):
    if current_record.get('date') and current_record.get('soap_section') and content_buffer.strip():
        record = {
            'date': current_record['date'],
            'department': current_record.get('department', ''),
            'time': current_record.get('time', ''),
            'soap_section': current_record['soap_section'],
            'content': content_buffer.strip()
        }
        records.append(record)

    if new_record_data:
        current_record.update(new_record_data)

    return ""


def group_records_by_datetime(records):
    """
    同じdate、department、timeの記録をグループ化し、
    各SOAPセクションを別々のフィールドとして統合する
    F(フリー)とサ(サマリ)も独立したフィールドとして処理
    """
    grouped = defaultdict(dict)

    for record in records:
        # グループ化のキーを作成
        key = (record['date'], record['department'], record['time'])

        # SOAPセクションに応じてフィールド名を決定
        soap_section = record['soap_section']
        if soap_section == 'F':
            soap_field = 'F_content'
        elif soap_section == 'サ':
            soap_field = 'summary_content'
        else:
            soap_field = f"{soap_section}_content"

        # 基本情報を設定（まだ設定されていない場合）
        if 'date' not in grouped[key]:
            grouped[key]['date'] = record['date']
            grouped[key]['department'] = record['department']
            grouped[key]['time'] = record['time']

        # SOAPコンテンツを追加
        content = record['content'].strip()
        if soap_field in grouped[key]:
            # 既に同じSOAPセクションが存在する場合
            existing_content = grouped[key][soap_field]
            # 重複チェック: 同じ内容が既に含まれている場合は追加しない
            if content not in existing_content:
                grouped[key][soap_field] += "\n" + content
        else:
            grouped[key][soap_field] = content

    # 辞書から配列に変換
    result = list(grouped.values())

    # 日付と時間でソート
    result.sort(key=lambda x: (x['date'], x['time']))

    return result


def remove_duplicates(records):
    """
    完全に重複したレコードを除去する
    """
    seen_records = set()
    unique_records = []

    for record in records:
        # レコードを文字列として表現してハッシュ化可能にする
        record_str = json.dumps(record, sort_keys=True, ensure_ascii=False)

        if record_str not in seen_records:
            seen_records.add(record_str)
            unique_records.append(record)

    return unique_records


def parse_medical_text(text):
    records = []
    current_record = {}
    content_buffer = ""

    date_pattern = re.compile(r"(\d{4}/\d{2}/\d{2}\(.?\))(?:\s*（入院\s*(\d+)\s*日目）)?")
    entry_pattern = re.compile(r"(.+?)\s+(.+?)\s+(.+?)\s+(\d{2}:\d{2})")
    soap_pattern = re.compile(r"([SOAPFサ])\s*>")

    for line in StringIO(text):
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.match(line)
        if date_match:
            content_buffer = process_record(current_record, content_buffer, records, {'date': date_match.group(1)})
            continue

        entry_match = entry_pattern.match(line)
        if entry_match and current_record.get('date'):
            content_buffer = process_record(current_record, content_buffer, records, {
                'department': entry_match.group(1).strip(),
                'time': entry_match.group(4).strip()
            })
            continue

        soap_match = soap_pattern.match(line)
        if soap_match and current_record.get('department'):
            content_buffer = process_record(current_record, content_buffer, records,
                                            {'soap_section': soap_match.group(1)})
            continue

        if current_record.get('soap_section'):
            content_buffer += line + "\n"

    process_record(current_record, content_buffer, records)

    # 従来の重複除去
    unique_records = []
    seen_keys = set()

    for record in records:
        key = (record['date'], record['department'], record['time'], record['soap_section'], record['content'])

        if key not in seen_keys:
            seen_keys.add(key)
            unique_records.append(record)

    # 新機能: 同じdate、department、timeの記録をグループ化
    grouped_records = group_records_by_datetime(unique_records)

    # 最終的な重複除去
    final_records = remove_duplicates(grouped_records)

    return final_records