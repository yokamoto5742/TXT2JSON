import json
import os
import re
from io import StringIO
from collections import defaultdict
from datetime import datetime


def convert_to_timestamp(date_str, time_str):
    try:
        date_match = re.match(r"(\d{4})/(\d{2})/(\d{2})", date_str)
        if not date_match:
            return None

        year, month, day = date_match.groups()

        time_match = re.match(r"(\d{2}):(\d{2})", time_str)
        if not time_match:
            return None

        hour, minute = time_match.groups()

        timestamp = f"{year}-{month}-{day}T{hour}:{minute}:00Z"

        return timestamp
    except Exception:
        return None


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
    grouped = defaultdict(dict)

    for record in records:
        key = (record['date'], record['department'], record['time'])

        soap_section = record['soap_section']
        soap_mapping = {
            'S': 'subject',
            'O': 'object',
            'A': 'assessment',
            'P': 'plan',
            'F': 'comment',
            'サ': 'summary'
        }
        soap_field = soap_mapping.get(soap_section, f"{soap_section}_content")

        if 'timestamp' not in grouped[key]:
            timestamp = convert_to_timestamp(record['date'], record['time'])
            grouped[key]['timestamp'] = timestamp
            grouped[key]['department'] = record['department']

        content = record['content'].strip()
        if soap_field in grouped[key]:
            existing_content = grouped[key][soap_field]
            if content not in existing_content:
                grouped[key][soap_field] += "\n" + content
        else:
            grouped[key][soap_field] = content

    result = list(grouped.values())

    result.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '')

    return result


def remove_duplicates(records):
    seen_records = set()
    unique_records = []

    for record in records:
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

    unique_records = []
    seen_keys = set()

    for record in records:
        key = (record['date'], record['department'], record['time'], record['soap_section'], record['content'])

        if key not in seen_keys:
            seen_keys.add(key)
            unique_records.append(record)

    grouped_records = group_records_by_datetime(unique_records)

    final_records = remove_duplicates(grouped_records)

    return final_records
