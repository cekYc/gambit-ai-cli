cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
mkdir -p results-sinirsiz
python -u run.py --out results-sinirsiz --no-time-limit --plan queen:auto --only kod-yorumlayici,kod-csv,kod-bagimlilik,kod-turkce,hata-envanter,hata-tarih,okuma-mro,okuma-dekorator,okuma-asyncio,okuma-js-this,okuma-js-tip,sql-kategori-pay,sql-medyan,term-ini,ajan-veri-temizle,ajan-api-belgesi,mantik-algoritma,talimat-kisitli-metin >> results-sinirsiz/calisma.log 2>&1
python -u run.py --out results-sinirsiz --no-time-limit --plan king:off --only kod-semver,kod-yorumlayici,kod-csv,kod-bagimlilik,kod-kova-js,kod-turkce,kod-fark,hata-envanter,hata-tarih,hata-async-js,hata-onbellek,okuma-mro,okuma-uretec,okuma-dekorator,okuma-asyncio,okuma-js-this,okuma-js-tip,sql-net-satis,sql-kategori-pay,sql-ardisik-ay,sql-medyan,term-log-rapor,term-arsiv,term-ini,term-kopyalar,ajan-kutuphane,ajan-yeniden-adlandir,ajan-veri-temizle,ajan-hata-izi,ajan-api-belgesi,mantik-olasilik,mantik-algoritma,mantik-bulmaca,inceleme-mantik-js >> results-sinirsiz/calisma.log 2>&1
echo BITTI >> results-sinirsiz/calisma.log
