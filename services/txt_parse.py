import json
import os
import re
from io import StringIO


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


def parse_medical_text(text):
    records = []
    current_record = {}
    content_buffer = ""

    date_pattern = re.compile(r"(\d{4}/\d{2}/\d{2}\(.?\))(?:\s*（入院\s*(\d+)\s*日目）)?")
    entry_pattern = re.compile(r"(.+?)\s+(.+?)\s+(.+?)\s+(\d{2}:\d{2})")
    soap_pattern = re.compile(r"([SOAPF])\s*>")

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

    return unique_records
