import os, shutil

base = r'C:\\AI\\benchmark\\v2\\results-umay\\sandboxes\\umay-akilli__kapali\\term-arsiv'
gelen = os.path.join(base, 'gelen')
arsiv = os.path.join(base, 'arsiv')
tarihsiz = os.path.join(arsiv, 'tarihsiz')

if os.path.exists(tarihsiz):
    for f in os.listdir(tarihsiz):
        src = os.path.join(tarihsiz, f)
        if os.path.isfile(src):
            dst = os.path.join(gelen, f)
            shutil.move(src, dst)
    for d in os.listdir(tarihsiz):
        src = os.path.join(tarihsiz, d)
        if os.path.isdir(src):
            dst = os.path.join(gelen, d)
            shutil.move(src, dst)
    tatil_src = os.path.join(tarihsiz, 'tatil')
    if os.path.exists(tatil_src):
        os.makedirs(os.path.join(gelen, 'tatil'), exist_ok=True)
        for f in os.listdir(tatil_src):
            shutil.move(os.path.join(tatil_src, f), os.path.join(gelen, 'tatil', f))
    shutil.rmtree(tarihsiz)

print('Geri tasindi')
