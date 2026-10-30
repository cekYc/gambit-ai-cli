# kod-sure-js · puan 0.45

**Not:** 5/11 test; başarısız: S.parseDuration("1h 30m 15s") === 5415 -> TypeError: Assignment to constant variable. | S.parseDuration("45m") === 2700 -> TypeError: Assignment to constant variable. | S.parseDuration("2h") === 7200 -> TypeError: Assignment to constant variable. | S.parseDuration("90s") === 90 -> TypeError: Assignment to constant variable. | S.parseDuration("1h15s") === 3615 -> TypeError: Assignment to constant v

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Cevap

```javascript
/**
 * "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi metinleri toplam saniyeye çevirir.
 * Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve sırayla gelir; aralarında boşluk olabilir veya olmayabilir.
 * Geçersiz girdide Error fırlatır.
 */
function parseDuration(str) {
  if (typeof str !== 'string') {
    throw new Error('Girdi bir metin olmalıdır.');
  }

  const trimmed = str.trim();
  
  // Boş metin kontrolü
  if (trimmed.length === 0) {
    throw new Error('Metin boş olamaz.');
  }

  // Düzenli ifade: Opsiyonel h, m, s birimlerinden oluşan sıralı yapısı.
  // Her birim: pozitif tam sayı + harf. Birimler arasında opsiyonel boşluklar var.
  const pattern = /^(\s*)(\d+h)?(\s*(\d+m))?(\s*(\d+s))?\s*$/;
  
  // Daha katı bir yaklaşım: Adım adım ayıralım ve doğrulayalım.
  // Önce metni parçalamak yerine, regex ile yakalayalım ama sırası ve tekrarını kontrol edelim.
  
  // Basitçe: Metinde sadece [0-9 hms] karakterleri olmalı (boşluklar hariç)
  if (!/^[0-9hms\s]+$/.test(trimmed)) {
    throw new Error('Metin geçersiz karakterler içeriyor.');
  }

  // Birimleri sırasıyla ayıralım.
  const order = ['h', 'm', 's'];
  let currentIndex = trimmed.length;
  const parts = {};

  for (let i = 0; i < order.length; i++) {
    const unit = order[i];
    // Bu birim metinde var mı? En sondan değil, baştan ilerliyoruz.
    
    // Şu ana kadar işlenmemiş kalan metin: trimmed.substring(0, currentIndex)
    let remaining = trimmed.slice(0, currentIndex);
    
    if (remaining.length === 0) {
      break;
    }

    // Kalan metinde bu birim var mı?
    const idxUnit = remaining.indexOf(unit);
    
    if (idxUnit !== -1) {
      // Birimden önceki kısım sayı olmalı
      const numStr = remaining.slice(0, idxUnit).trim();
      
      // Sayı kısmı boş olmamalı ve sadece rakamlardan oluşmalı
      if (numStr.length === 0 || !/^\d+$/.test(numStr)) {
        throw new Error(`Birimi "${unit}" için geçerli bir sayı bulunamadı.`);
      }

      // Tekrar kontrolü: parts içinde zaten var mı? Regex ile zaten sıralı gidiyoruz, ama emin olalım.
      if (parts[unit] !== undefined) {
        throw new Error(`Birim "${unit}" tekrarlanmış.`);
      }

      parts[unit] = parseInt(numStr, 10);

      // Birimi ve sayısını kaldırdık, kalan metni güncelle
      const afterUnit = remaining.slice(idxUnit + 1);
      currentIndex -= (remaining.length - afterUnit.length);
      // Aslında daha basit: trimmed'i güncelleyelim
      trimmed = afterUnit;
      
    } else {
      // Bu birim yok, devam et. Ama dikkat: Eğer önceki birimler yoksa ve bu birim varsa?
      // Regex yaklaşımı bunu otomatik yapar mı? 
      // Örnek: "30m" -> h yok, m var. 
      // Üsteki döngüde: i=0 (h), remaining=" 30m" (trimmed olmuşsa "30m"), indexOf('h') = -1. parts.h atanmaz.
      // i=1 (m), remaining="30m", indexOf('m')=2. numStr="30". parts.m=30. trimmed="".
      // i=2 (s), remaining="", break.
      // Bu çalışıyor.
      
      // Peki "90s" için?
      // i=0 (h): remaining="90s", no h. 
      // i=1 (m): remaining="90s", no m.
      // i=2 (s): remaining="90s", s found at 2. numStr="90". parts.s=90. trimmed="".
      // Çalışıyor.
      
      // Peki "1h 30m" ?
      // trimmed = "1h 30m"
      // i=0 (h): remaining="1h 30m", h at 1. numStr="1". parts.h=1. trimmed=" 30m". trim -> " 30m" (dikkat: slice(2) = " 30m")
      // i=1 (m): remaining=" 30m". indexOf('m')=3. numStr=" 30".trim()="30". parts.m=30. trimmed = remaining.slice(4) = "".
      // i=2 (s): remaining="", break.
      // Çalışıyor.
    }
  }

  // İşlem bittikten sonra kalan metin boş olmalı. Değilse geçersiz karakter veya sıralama hatası var.
  if (trimmed.trim().length !== 0) {
    throw new Error('Metin tamamen işlenemedi, geçersiz format.');
  }

  // Hiçbir birim yoksa? Örn: "abc" yukarıda yakalanır. Ama "123"? 
  // "123" -> i=0(h) no h. i=1(m) no m. i=2(s) no s. trimmed="123". Son kontrol: length != 0 -> Error. Doğru.
  
  if (Object.keys(parts).length === 0) {
    throw new Error('Geçerli bir süre birimi bulunamadı.');
  }

  let totalSeconds = 0;
  if ('h' in parts) totalSeconds += parts['h'] * 3600;
  if ('m' in parts) totalSeconds += parts['m'] * 60;
  if ('s' in parts) totalSeconds += parts['s'];

  return totalSeconds;
}

module.exports = { parseDuration };

## Notlandırılan kod/komut

```
/**
 * "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi metinleri toplam saniyeye çevirir.
 * Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve sırayla gelir; aralarında boşluk olabilir veya olmayabilir.
 * Geçersiz girdide Error fırlatır.
 */
function parseDuration(str) {
  if (typeof str !== 'string') {
    throw new Error('Girdi bir metin olmalıdır.');
  }

  const trimmed = str.trim();
  
  // Boş metin kontrolü
  if (trimmed.length === 0) {
    throw new Error('Metin boş olamaz.');
  }

  // Düzenli ifade: Opsiyonel h, m, s birimlerinden oluşan sıralı yapısı.
  // Her birim: pozitif tam sayı + harf. Birimler arasında opsiyonel boşluklar var.
  const pattern = /^(\s*)(\d+h)?(\s*(\d+m))?(\s*(\d+s))?\s*$/;
  
  // Daha katı bir yaklaşım: Adım adım ayıralım ve doğrulayalım.
  // Önce metni parçalamak yerine, regex ile yakalayalım ama sırası ve tekrarını kontrol edelim.
  
  // Basitçe: Metinde sadece [0-9 hms] karakterleri olmalı (boşluklar hariç)
  if (!/^[0-9hms\s]+$/.test(trimmed)) {
    throw new Error('Metin geçersiz karakterler içeriyor.');
  }

  // Birimleri sırasıyla ayıralım.
  const order = ['h', 'm', 's'];
  let currentIndex = trimmed.length;
  const parts = {};

  for (let i = 0; i < order.length; i++) {
    const unit = order[i];
    // Bu birim metinde var mı? En sondan değil, baştan ilerliyoruz.
    
    // Şu ana kadar işlenmemiş kalan metin: trimmed.substring(0, currentIndex)
    let remaining = trimmed.slice(0, currentIndex);
    
    if (remaining.length === 0) {
      break;
    }

    // Kalan metinde bu birim var mı?
    const idxUnit = remaining.indexOf(unit);
    
    if (idxUnit !== -1) {
      // Birimden önceki kısım sayı olmalı
      const numStr = remaining.slice(0, idxUnit).trim();
      
      // Sayı kısmı boş olmamalı ve sadece rakamlardan oluşmalı
      if (numStr.length === 0 || !/^\d+$/.test(numStr)) {
        throw new Error(`Birimi "${unit}" için geçerli bir sayı bulunamadı.`);
      }

      // Tekrar kontrolü: parts içinde zaten var mı? Regex ile zaten sıralı gidiyoruz, ama emin olalım.
      if (parts[unit] !== undefined) {
        throw new Error(`Birim "${unit}" tekrarlanmış.`);
      }

      parts[unit] = parseInt(numStr, 10);

      // Birimi ve sayısını kaldırdık, kalan metni güncelle
      const afterUnit = remaining.slice(idxUnit + 1);
      currentIndex -= (remaining.length - afterUnit.length);
      // Aslında daha basit: trimmed'i güncelleyelim
      trimmed = afterUnit;
      
    } else {
      // Bu birim yok, devam et. Ama dikkat: Eğer önceki birimler yoksa ve bu birim varsa?
      // Regex yaklaşımı bunu otomatik yapar mı? 
      // Örnek: "30m" -> h yok, m var. 
      // Üsteki döngüde: i=0 (h), remaining=" 30m" (trimmed olmuşsa "30m"), indexOf('h') = -1. parts.h atanmaz.
      // i=1 (m), remaining="30m", indexOf('m')=2. numStr="30". parts.m=30. trimmed="".
      // i=2 (s), remaining="", break.
      // Bu çalışıyor.
      
      // Peki "90s" için?
      // i=0 (h): remaining="90s", no h. 
      // i=1 (m): remaining="90s", no m.
      // i=2 (s): remaining="90s", s found at 2. numStr="90". parts.s=90. trimmed="".
      // Çalışıyor.
      
      // Peki "1h 30m" ?
      // trimmed = "1h 30m"
      // i=0 (h): remaining="1h 30m", h at 1. numStr="1". parts.h=1. trimmed=" 30m". trim -> " 30m" (dikkat: slice(2) = " 30m")
      // i=1 (m): remaining=" 30m". indexOf('m')=3. numStr=" 30".trim()="30". parts.m=30. trimmed = remaining.slice(4) = "".
      // i=2 (s): remaining="", break.
      // Çalışıyor.
    }
  }

  // İşlem bittikten sonra kalan metin boş olmalı. Değilse geçersiz karakter veya sıralama hatası var.
  if (trimmed.trim().length !== 0) {
    throw new Error('Metin tamamen işlenemedi, geçersiz format.');
  }

  // Hiçbir birim yoksa? Örn: "abc" yukarıda yakalanır. Ama "123"? 
  // "123" -> i=0(h) no h. i=1(m) no m. i=2(s) no s. trimmed="123". Son kontrol: length != 0 -> Error. Doğru.
  
  if (Object.keys(parts).length === 0) {
    throw new Error('Geçerli bir süre birimi bulunamadı.');
  }

  let totalSeconds = 0;
  if ('h' in parts) totalSeconds += parts['h'] * 3600;
  if ('m' in parts) totalSeconds += parts['m'] * 60;
  if ('s' in parts) totalSeconds += parts['s'];

  return totalSeconds;
}

module.exports = { parseDuration };
```
