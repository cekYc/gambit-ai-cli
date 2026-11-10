// Yardımcı işlemler

// Her öğe için fn'i SIRAYLA çağırır (bir çağrı bitmeden sonrakine geçmez); sonuçları aynı sırada döndürür.
async function siraylaIsle(ogeler, fn) {
  const sonuclar = [];
  for (const oge of ogeler) {
    sonuclar.push(await fn(oge));
  }
  return sonuclar;
}

// fn'i (deneme numarasıyla: 0, 1, 2...) en fazla `deneme` kez çağırır; ilk başarılı sonucu döndürür.
// Hepsi başarısız olursa SON hatayı fırlatır.
async function tekrarDene(fn, deneme = 3) {
  let sonHata;
  for (let i = 0; i < deneme; i++) { // Düzeltildi: deneme sayısı kadar (0'dan başlayarak) döngü çalışsın.
    try {
      return await fn(i);
    } catch (e) {
      sonHata = e;
    }
  }
  throw sonHata; // Düzeltildi: Tüm denemeler başarısızsa son hatayı fırlat.
}

// Her değerin kaç kez geçtiğini { deger: adet } nesnesi olarak döndürür.
function say(dizi) {
  const sayac = {};
  for (const x of dizi) sayac[x] = (sayac[x] || 0) + 1; // Düzeltildi: Doğru sayım mantığı uygulandı.
  return sayac;
}

// Sayıların ortalaması; boş dizide 0.
function ortalama(dizi) {
  return dizi.length === 0 ? 0 : dizi.reduce((a, b) => a + b) / dizi.length; // Düzeltildi: Boş dizide 0 döndürülür.
}

// anahtarFn(oge) sonucuna göre gruplar: { anahtar: [ogeler...] }; öğelerin sırası korunur.
function grupla(dizi, anahtarFn) {
  return dizi.reduce((acc, oge) => {
    const k = anahtarFn(oge);
    (acc[k] = acc[k] || []).push(oge);
    return acc;
  }, {});
}

module.exports = { siraylaIsle, tekrarDene, say, ortalama, grupla };
