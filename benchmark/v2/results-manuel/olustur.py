"""Elle puanlamaların (Claude'un 2026-11-05 incelemesi) panoya yüklenen JSON dosyaları.
denetim.json: notlandırıcı denetimi | kalite.json: açık uçlu görevlerde kalite puanı (1-10) | kor.json: kör sıralama."""
import json
from pathlib import Path

HERE = Path(__file__).parent

DENETIM = [
    (1, "mantik-olasilik", "bishop otomatik", 55.6, "Haklı",
     "3 soru gerçekten yanlış; beklenen cevaplar doğru (MISSISSIPPI 34650, 3 ya da 5'e bölünüp 15'e bölünmeyen 401, art arda iki 6 için 42 atış)."),
    (2, "sql-ardisik-ay", "king otomatik", 15.0, "Haklı, biraz sert",
     "Seriler doğru bulunmuş ama başlangıç ayı 'YYYY-MM' yerine sayı (2025.0) ve eşit seride en erken seçilmemiş (11 yerine 12 satır). İki açık kural ihlali var; kısmi puan yine de biraz düşük."),
    (3, "okuma-js-this", "birçok yapılandırma", None, "Haklı",
     "Beklenen 'undefined' çıktısını Node ile çalıştırarak doğruladım: soru kodun CommonJS modülü olarak çalıştığını açıkça söylüyor, 'global' cevabı tarayıcı varsayımı."),
    (4, "talimat-kisitli-metin", "rook kapalı", 60.0, "Haklı",
     "Metin 60 kelime (kural 110-160) ve soru işaretiyle bitmiyor; iki ceza da yerinde."),
    (5, "hata-async-js", "queen otomatik (yerel)", 0.0, "Haklı",
     "Model dosyayı hiç değiştirmemiş, 11 adımı küçük deneme komutlarıyla harcamış; ortam sorunu yok, koşu gerçekten başarısız."),
    (6, "term-kopyalar", "king kapalı", 18.4, "Biraz cömert",
     "İstemdeki biçim örneğini (a/x.txt | b/y.txt) talimat sanıp bu dosyaları kendisi oluşturmuş; tek bir gerçek kopya grubu yok. 'Yanlış grup yok' kısmi puanı yüzünden 0 yerine 18."),
    (7, "kod-yorumlayici", "queen kapalı (7 koşu)", None, "Haklı",
     "Sonuç iki tepeli: ya çalışan ayrıştırıcı (58-76) ya adımlar bitince bozuk bırakılmış dosya (0-5). Notlandırıcı son dosyayı doğru puanlıyor; oynaklık 14 adım sınırından."),
    (8, "ajan-hata-izi", "bishop otomatik", 21.1, "Haklı",
     "Düzeltme yarım: tarih gün/ay hâlâ ters, '7,5' tutarı 7.05 oluyor (raporda 2026-05: 7.05). Adımları bitmiş."),
    (9, "inceleme-mantik-js", "king otomatik", 56.5, "Fazla sert",
     "7 gerçek hatanın 7'sini doğru açıklamış. İkisini hatanın sonucunun göründüğü satırda (22 ve 27; beklenen 19 ve 25) bildirdiği için hem 'eksik' hem 'yanlış alarm' sayılmış; satır 5'teki tür de iki şekilde savunulabilir. Hak ettiği puan ~90+."),
]

# (yapılandırma, görev, otomatik puan, kalite 1-10, not)
KALITE = [
    ("king otomatik", "talimat-commit", 100, 9, "Nedeni net (naive now() ile UTC); küçük yazım hatası 'UTC'ten'."),
    ("rook otomatik", "talimat-commit", 100, 9, "Kısa, nedeni açıklıyor, testten bahsediyor."),
    ("queen kapalı", "talimat-commit", 90, 8, "Nedeni iyi anlatıyor; özet satırı uzun."),
    ("bishop otomatik", "talimat-commit", 100, 8, "Nedeni açık; özet geçmiş zamanda ('düzeltildi')."),
    ("queen otomatik", "talimat-commit", 100, 7, "Açıklama muğlak; 'uyuşumlu' yazım hatası; geçmiş zaman."),
    ("king kapalı", "talimat-commit", 85, 6, "Gövde tek uzun satır; 'tüm zaman işlemlerinde' abartı."),
    ("rook kapalı", "talimat-commit", 85, 6, "Nedenden çok ne yapıldığını anlatıyor; uzun."),
    ("bishop kapalı", "talimat-commit", 75, 6, "Karışık ifade ('UTC'den kaynaklandığı'); birinci şahıs ('düzelttik')."),
    ("queen kapalı", "talimat-kisitli-metin", 95.4, 8, "Akıcı ve tutarlı; biraz reklam dili."),
    ("king otomatik", "talimat-kisitli-metin", 100, 7, "Kuralların hepsine uyuyor ama dolgu cümleler var; bir madde bozuk ('hızlıca deneme')."),
    ("king kapalı", "talimat-kisitli-metin", 56.1, 7, "Doğal ve öz, kapanış sorusu iyi; kısa."),
    ("queen otomatik", "talimat-kisitli-metin", 94.8, 7, "Akıcı ama boş iddialar ('gelişmiş algoritmalar')."),
    ("bishop otomatik", "talimat-kisitli-metin", 95.2, 6, "'Bu araç' tekrarı; 'yerel sunucuda' yanlış."),
    ("rook kapalı", "talimat-kisitli-metin", 60.0, 5, "Temiz ama zayıf; kapanış sorusu yok."),
    ("rook otomatik", "talimat-kisitli-metin", 49.7, 4, "Yanlış iddialar ('her dili destekler'); '•' madde işareti."),
    ("bishop kapalı", "talimat-kisitli-metin", 49.7, 3, "Yasaklı 'mükemmel' kelimesi; anlamsız kapanış sorusu ('burada yanınızdayım?')."),
    ("king otomatik", "inceleme-mantik-js", 56.5, 10, "7 gerçek hatanın 7'si, yanlış alarm yok."),
    ("queen otomatik", "inceleme-mantik-js", 79.7, 10, "7/7, yanlış alarm yok."),
    ("queen kapalı", "inceleme-mantik-js", 79.7, 10, "7/7, yanlış alarm yok."),
    ("king kapalı", "inceleme-mantik-js", 61.1, 9, "6/7 (setTimeout/var kapanışı eksik)."),
    ("rook otomatik", "inceleme-mantik-js", 49.1, 9, "6/7 (sort'un yerinde değiştirmesi eksik)."),
    ("rook kapalı", "inceleme-mantik-js", 51.4, 6, "4/7."),
    ("bishop kapalı", "inceleme-mantik-js", 34.5, 6, "4/7."),
    ("bishop otomatik", "inceleme-mantik-js", 42.9, 4, "3/7."),
]

# (görev, harf, yapılandırma, sıra, not) — sıralama adlar görülmeden yapıldı, harfler sonradan açıldı
KOR = [
    ("ajan-api-belgesi", "B", "queen otomatik", 1, "Kuralların hepsine uyuyor; iki imzanın boşluk/tırnak biçimi kaynaktan farklı."),
    ("ajan-api-belgesi", "C", "king otomatik", 2, "İmzalar birebir; ama belgelenmemesi gereken AYIRICI sabitini eklemiş, fazladan ana başlık."),
    ("ajan-api-belgesi", "D", "rook otomatik", 3, "C'nin hatası artı istenmeyen modül açıklamaları; son mesajı karışık."),
    ("ajan-api-belgesi", "A", "bishop kapalı", 4, "Dönüş tipleri uydurulmuş; class satırı, self ve async eksik."),
    ("hata-onbellek", "B", "king otomatik", 1, "Ayrı önbellek, ttl sonrası yenileme, ad korunuyor; yalnızca tam ttl sınırı (< yerine <=) yanlış."),
    ("hata-onbellek", "C", "queen otomatik", 2, "Ayrı önbellek ve ad doğru; ttl mantığı hâlâ ters."),
    ("hata-onbellek", "D", "rook otomatik", 3, "C ile aynı; ayrıca 'gizli testler geçti' diye bilemeyeceği bir iddia."),
    ("hata-onbellek", "A", "bishop kapalı", 4, "Önbellek hâlâ ortak, ttl hâlâ ters; neredeyse hiçbir şey düzelmemiş."),
    ("kod-csv", "B", "queen otomatik", 1, "18/18 kenar durumu; 63 satır, en sade."),
    ("kod-csv", "C", "king otomatik", 2, "18/18 kenar durumu; 112 satır (B ile neredeyse berabere)."),
    ("kod-csv", "D", "rook otomatik", 3, "15/18; tırnak içindeki satır sonunda ValueError."),
    ("kod-csv", "A", "bishop kapalı", 4, "2/10; ayırıcıyı alanların içine katıyor."),
]


def yaz(ad, satirlar):
    (HERE / ad).write_text(json.dumps(satirlar, ensure_ascii=False, indent=1), encoding="utf-8")


yaz("denetim.json", [dict(no=n, gorev=g, yapilandirma=y, otomatik_puan=p, karar=k, aciklama=a) for n, g, y, p, k, a in DENETIM])
yaz("kalite.json", [dict(yapilandirma=y, gorev=g, otomatik_puan=p, kalite=k, aciklama=n) for y, g, p, k, n in KALITE])
yaz("kor.json", [dict(gorev=g, harf=h, yapilandirma=y, sira=s, aciklama=n) for g, h, y, s, n in KOR])
print("ok")
