import re
import json
import os
from io import StringIO


def parse_medical_text(text):
    records = []
    current_record = {}
    content_buffer = ""

    date_pattern = re.compile(r"(\d{4}/\d{2}/\d{2}\(.?\))(?:\s*（入院\s*(\d+)\s*日目）)?")
    entry_pattern = re.compile(r"(.+?)\s+(.+?)\s+(.+?)\s+(\d{2}:\d{2})")
    soap_pattern = re.compile(r"([SOAPF])\s*>")

    def save_current_record():
        if current_record.get('date') and current_record.get('soap_section') and content_buffer.strip():
            record = {
                'date': current_record['date'],
                'department': current_record.get('department', ''),
                'time': current_record.get('time', ''),
                'soap_section': current_record['soap_section'],
                'content': content_buffer.strip()
            }
            records.append(record)

    for line in StringIO(text):
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.match(line)
        if date_match:
            save_current_record()
            current_record = {'date': date_match.group(1)}
            content_buffer = ""
            continue

        entry_match = entry_pattern.match(line)
        if entry_match and current_record.get('date'):
            save_current_record()
            current_record = {
                'date': current_record['date'],
                'department': entry_match.group(1).strip(),
                'time': entry_match.group(4).strip()
            }
            content_buffer = ""
            continue

        soap_match = soap_pattern.match(line)
        if soap_match and current_record.get('department'):
            save_current_record()
            current_record['soap_section'] = soap_match.group(1)
            content_buffer = ""
            continue

        if current_record.get('soap_section'):
            content_buffer += line + "\n"

    save_current_record()

    return records


def main():
    base_dir = r"C:\Shinseikai\TXT2JSON"
    input_file = os.path.join(base_dir, "sample.txt")
    output_file = os.path.join(base_dir, "parsed_medical_data.json")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            medical_text = f.read()

        parsed_data = parse_medical_text(medical_text)

        print(json.dumps(parsed_data, indent=2, ensure_ascii=False))

        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(parsed_data, outfile, indent=2, ensure_ascii=False)

        print(f"\n解析結果を {output_file} に保存しました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
