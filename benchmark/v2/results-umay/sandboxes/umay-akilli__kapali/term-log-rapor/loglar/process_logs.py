import os, re, csv

log_dir = 'loglar'
results = []

for root, dirs, files in os.walk(log_dir):
    for file in files:
        if file.endswith('.log') and not re.search(r'\.log\.', file):
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, log_dir).replace('\\', '/')
            
            error_count = 0
            warn_count = 0
            info_count = 0
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(' ', 3)
                        if len(parts) >= 3:
                            level = parts[2]
                            if level == 'ERROR':
                                error_count += 1
                            elif level == 'WARN':
                                warn_count += 1
                            elif level == 'INFO':
                                info_count += 1
            except Exception as e:
                print('Hata: ' + filepath + ' - ' + str(e))
            
            results.append({
                'dosya': rel_path,
                'error': error_count,
                'warn': warn_count,
                'info': info_count
            })

# Sıralama: error azalan, sonra dosya yolu artan
results.sort(key=lambda x: (-x['error'], x['dosya']))

# CSV yaz
with open('loglar/rapor.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['dosya', 'error', 'warn', 'info'])
    for r in results:
        writer.writerow([r['dosya'], r['error'], r['warn'], r['info']])

for r in results:
    print(r['dosya'] + ': error=' + str(r['error']) + ', warn=' + str(r['warn']) + ', info=' + str(r['info']))

print('rapor.csv oluşturuldu.')
