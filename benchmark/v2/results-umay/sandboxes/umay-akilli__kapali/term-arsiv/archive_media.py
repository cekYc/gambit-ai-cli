import os, re, shutil

base = r'C:\\AI\\benchmark\\v2\\results-umay\\sandboxes\\umay-akilli__kapali\\term-arsiv'
gelen = os.path.join(base, 'gelen')
arsiv = os.path.join(base, 'arsiv')

os.makedirs(arsiv, exist_ok=True)

media_ext = {'.jpg', '.jpeg', '.png', '.mp4', '.mov'}
# YYYYMMDD (8 rakam, 20 ile başlayan) veya YYYY-MM-DD
date_pattern = re.compile(r'(20\d{6})|(\d{4}-\d{2}-\d{2})')

moved = []
for root, dirs, files in os.walk(gelen):
    for f in files:
        src = os.path.join(root, f)
        ext = os.path.splitext(f)[1].lower()
        if ext not in media_ext:
            continue
        
        m = date_pattern.search(f)
        if m:
            date_str = m.group(1) if m.group(1) else m.group(2)
            if '-' in date_str:
                year, month = date_str.split('-')[:2]
            else:
                year = date_str[:4]
                month = date_str[4:6]
            dest_dir = os.path.join(arsiv, year, month)
        else:
            dest_dir = os.path.join(arsiv, 'tarihsiz')
        
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f)
        
        shutil.move(src, dest)
        moved.append((src, dest))

print(f'Tasinan: {len(moved)}')
for s, d in moved:
    print(f'  {s} -> {d}')
