// Yardımcı işlemler

// Her öğe için fn'i SIRAYLA çağırır (bir çağrı bitmeden sonrakine geçmez); sonuçları aynı sırada döndürür.
async function siraylaIsle(ogeler, fn) {
  const promises = ogeler.map(async (oge) => fn(oge));
  return await Promise.all(promises);
}

// fn'i (deneme numarasıyla: 0, 1, 2...) en fazla `deneme` kez çağırır; ilk başarılı sonucu döndürür.
// Hepsi başarısız olursa SON hatayı fırlatır.
async function tekrarDene(fn, deneme = 3) {
  let sonHata;
  // Deneme sayısı deneme+1 adettir (0'dan deneme'ye kadar)
  for (let i = 0; i <= deneme; i++) {
    try {
      return await fn(i);
    } catch (e) {
      sonHata = e;
    }
  }
  // Tüm denemeler başarısız olursa en son hatayı fırlat
  throw sonHata;
}

// Her değerin kaç kez geçtiğini { deger: adet } nesnesi olarak döndürür.
function say(dizi) {
  const sayac = {};
  for (const x of dizi) sayac[x] = (sayac[x] || 0) + 1;
  return sayac;
}

// Sayıların ortalaması; boş dizide 0.
function ortalama(dizi) {
  if (dizi.length === 0) {
    return 0;
  }
  return dizi.reduce((a, b) => a + b) / dizi.length;
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