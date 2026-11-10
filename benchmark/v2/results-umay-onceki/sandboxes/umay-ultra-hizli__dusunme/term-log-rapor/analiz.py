import os
import csv
import re

log_dir = 'loglar'
records = []

for root, dirs, files in os.walk(log_dir):
    for f in files:
        if not f.endswith('.log'):
            continue
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, log_dir).replace(os.sep, '/')
        
        error = 0
        warn = 0
        info = 0
        
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    level = parts[2]
                    if level == 'ERROR':
                        error += 1
                    elif level == 'WARN':
                        warn += 1
                    elif level == 'INFO':
                        info += 1
        
        records.append({'dosya': rel_path, 'error': error, 'warn': warn, 'info': info})

# Sort: error descending, then file path ascending
records.sort(key=lambda x: (-x['error'], x['dosya']))

with open('rapor.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['dosya', 'error', 'warn', 'info'])
    writer.writeheader()
    writer.writerows(records)

print('CSV created successfully')
print(f'Records: {len(records)}')
for r in records:
    print(f"{r['dosya']}: E={r['error']}, W={r['warn']}, I={r['info']}")
