import json
import os
import re
from io import StringIO


def save_current_record(current_record, content_buffer, records):
    if current_record.get('date') and current_record.get('soap_section') and content_buffer.strip():
        record = {
            'date': current_record['date'],
            'department': current_record.get('department', ''),
            'time': current_record.get('time', ''),
            'soap_section': current_record['soap_section'],
            'content': content_buffer.strip()
        }
        records.append(record)


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
            save_current_record(current_record, content_buffer, records)
            current_record = {'date': date_match.group(1)}
            content_buffer = ""
            continue

        entry_match = entry_pattern.match(line)
        if entry_match and current_record.get('date'):
            save_current_record(current_record, content_buffer, records)
            current_record = {
                'date': current_record['date'],
                'department': entry_match.group(1).strip(),
                'time': entry_match.group(4).strip()
            }
            content_buffer = ""
            continue

        soap_match = soap_pattern.match(line)
        if soap_match and current_record.get('department'):
            save_current_record(current_record, content_buffer, records)
            current_record['soap_section'] = soap_match.group(1)
            content_buffer = ""
            continue

        if current_record.get('soap_section'):
            content_buffer += line + "\n"

    save_current_record(current_record, content_buffer, records)

    return records
