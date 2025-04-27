import re
import json
import io

def parse_medical_text(text):
    records = []
    current_date = None
    current_days_in_hospital = None
    current_entry_info = {}
    current_soap_section = None
    content_buffer = ""

    date_pattern = re.compile(r"(\d{4}/\d{2}/\d{2}\(.?\))\s*（入院\s*(\d+)\s*日目）")
    entry_pattern = re.compile(r"(.+?)\s+(.+?)\s+(.+?)\s+(\d{2}:\d{2})")
    soap_pattern = re.compile(r"([SOAPF])\s*>")

    for line in io.StringIO(text):
        line = line.strip()
        if not line:
            continue

        date_match = date_pattern.match(line)
        entry_match = entry_pattern.match(line)
        soap_match = soap_pattern.match(line)

        if date_match:
            if current_entry_info and current_soap_section and content_buffer.strip():
                record = current_entry_info.copy()
                record['soap_section'] = current_soap_section
                record['content'] = content_buffer.strip()
                if 'doctor' in record: del record['doctor']
                if 'insurance' in record: del record['insurance']
                records.append(record)

            current_date = date_match.group(1)
            current_days_in_hospital = int(date_match.group(2))
            current_entry_info = {}
            current_soap_section = None
            content_buffer = ""
            continue

        elif entry_match and current_date:
            if current_entry_info and current_soap_section and content_buffer.strip():
                record = current_entry_info.copy()
                record['soap_section'] = current_soap_section
                record['content'] = content_buffer.strip()
                if 'doctor' in record: del record['doctor']
                if 'insurance' in record: del record['insurance']
                records.append(record)

            current_entry_info = {
                'date': current_date,
                'days_in_hospital': current_days_in_hospital,
                'department': entry_match.group(1).strip(),
                '_doctor_temp': entry_match.group(2).strip(),
                '_insurance_temp': entry_match.group(3).strip(),
                'time': entry_match.group(4).strip()
            }
            current_soap_section = None
            content_buffer = ""
            continue

        elif soap_match and current_entry_info:
            if current_soap_section and content_buffer.strip():
                record = current_entry_info.copy()
                record['soap_section'] = current_soap_section
                record['content'] = content_buffer.strip()
                if '_doctor_temp' in record: del record['_doctor_temp']
                if '_insurance_temp' in record: del record['_insurance_temp']
                if 'doctor' in record: del record['doctor']
                if 'insurance' in record: del record['insurance']
                records.append(record)

            current_soap_section = soap_match.group(1)
            content_buffer = ""
            continue

        elif current_soap_section and current_entry_info:
            content_buffer += line + "\n"

    if current_entry_info and current_soap_section and content_buffer.strip():
        record = current_entry_info.copy()
        record['soap_section'] = current_soap_section
        record['content'] = content_buffer.strip()
        if '_doctor_temp' in record: del record['_doctor_temp']
        if '_insurance_temp' in record: del record['_insurance_temp']
        if 'doctor' in record: del record['doctor']
        if 'insurance' in record: del record['insurance']
        records.append(record)

    final_records = []
    for record in records:
        record.pop('doctor', None)
        record.pop('insurance', None)
        record.pop('_doctor_temp', None)
        record.pop('_insurance_temp', None)
        final_records.append(record)

    return final_records

file_path = "C:\Shinseikai\TXT2JSON\sample.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        sample_text = f.read()

    parsed_data = parse_medical_text(sample_text) #
    json_output = json.dumps(parsed_data, indent=2, ensure_ascii=False) #
    print(json_output)

    output_file_path = "C:\Shinseikai\TXT2JSON\parsed_medical_data.json"
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(parsed_data, outfile, indent=2, ensure_ascii=False) #
    print(f"\n修正された解析結果を {output_file_path} に保存しました。")

except FileNotFoundError:
    print(f"エラー: ファイル '{file_path}' が見つかりません。") #
except Exception as e:
    print(f"エラーが発生しました: {e}") #
