# kod-sure-js · puan 0.45

**Not:** 5/11 test; başarısız: S.parseDuration("1h 30m 15s") === 5415 -> Error: Geçersiz girdi: Sayı eksik | S.parseDuration("45m") === 2700 -> Error: Geçersiz girdi: Sayı eksik | S.parseDuration("2h") === 7200 -> Error: Geçersiz girdi: Sayı eksik | S.parseDuration("90s") === 90 -> Error: Geçersiz girdi: Beklenmeyen format | S.parseDuration("1h15s") === 3615 -> TypeError: Assignment to constant variable.

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Cevap

```javascript
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error('Geçersiz girdi: Boş veya tip hatalı');
  }

  const units = ['h', 'm', 's'];
  let totalSeconds = 0;
  let lastUnitIndex = -1;

  // String'i boşluklara bölerek birimler ve sayıları ayır
  const parts = str.trim().split(/\s+/);

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    
    // "1h" şeklinde tek parça gelen durumlarda da işleme alınmalı.
    // Ancak gereksinimlerde "aralarında boşluk olabilir de olmayabilir de" denmiş.
    // Örneğin "2h" veya "45m". Regex ile bu şekilde yakalayalım mı? 
    // Daha güvenli bir yaklaşım: Her kelimenin sonunda birim var mı diye kontrol et.
    
    if (!part) continue;

    const numberMatch = part.match(/^(\d+)$/);
    const unitMatch = part.match(/([hm])$/i);

    if (unitMatch && !numberMatch) {
      // Sayısı olmayan birim örn: "h", "m"
      throw new Error('Geçersiz girdi: Sayı eksik');
    }

    if (!numberMatch && !unitMatch) {
      // Bilinmeyen format örn: "1abc" veya boşluk içinde başka şeyler varsa (parantez vb.)
      // Ancak prompt sadece h,m,s birimlerini belirtiyor. 
      // Güvenli olması için sadece sayı + birim yapısını bekleyelim.
      if (!part.match(/^\d+[hm]/i)) {
         throw new Error('Geçersiz girdi: Beklenmeyen format');
      }
    }

    let value = 0;
    const unitChar = (unitMatch || part.match(/[hm]/i))[1]; // Birim karakterini al

    if (!numberMatch) {
       numberMatch = part.match(/^(\d+)?/); // Sadece birim varsa sayıyı 0 kabul et ama yukarıda kontrol edildi. 
       // Düzeltme: Eğer unitMatch olduysa ve numberMatch yoksa, yukarıdaki hata fırlatılmış olmalı.
       // Bu kod bloğuna tekrar düşüyorsa, sayıya sahip olmasını sağla.
    }

    if (numberMatch) {
      value = parseInt(numberMatch[1], 10);
    } else {
      throw new Error('Geçersiz girdi: Sayı bulunamadı');
    }

    const unitIndex = units.indexOf(unitChar.toLowerCase());

    // Yanlış sıra veya tekrar eden birim kontrolü
    if (unitIndex === -1) {
      throw new Error(`Bilinmeyen birim: ${part}`);
    }

    if (unitIndex < 0 || lastUnitIndex !== -1 && unitIndex <= lastUnitIndex) {
       // Yanlış sıra (örn: m sonra h gelmesi -> index 1 sonra 0) veya tekrar eden birim
       // Sıralama: h(0), m(1), s(2). Sıra artmalı.
       if (unitIndex < lastUnitIndex + 1) {
         throw new Error('Yanlış sıra: Birimler h, m, s sırasıyla gelmelidir');
       }
    }

    // Birimi topla
    switch (unitChar.toLowerCase()) {
      case 'h': value *= 3600; break;
      case 'm': value *= 60; break;
      case 's': /* zaten saniye */ break;
      default: throw new Error('Bilinmeyen birim');
    }

    totalSeconds += value;
    
    if (unitIndex !== -1) {
      lastUnitIndex = unitIndex;
    } else {
      // Eğer sadece sayı gelse ve birim yoksa, bu gereksizdir ama hata fırlatıyoruz mu? 
      // Prompt: "sayısı olmayan birim" hatası. Sayı olmadan birim gelirse yukarıdaki mantıkla yakalanıyor.
      // Ancak "2h" formatında regex ile kontrol etmemiz daha iyisi.
    }
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error('Geçersiz girdi: Boş veya tip hatalı');
  }

  const units = ['h', 'm', 's'];
  let totalSeconds = 0;
  let lastUnitIndex = -1;

  // String'i boşluklara bölerek birimler ve sayıları ayır
  const parts = str.trim().split(/\s+/);

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    
    // "1h" şeklinde tek parça gelen durumlarda da işleme alınmalı.
    // Ancak gereksinimlerde "aralarında boşluk olabilir de olmayabilir de" denmiş.
    // Örneğin "2h" veya "45m". Regex ile bu şekilde yakalayalım mı? 
    // Daha güvenli bir yaklaşım: Her kelimenin sonunda birim var mı diye kontrol et.
    
    if (!part) continue;

    const numberMatch = part.match(/^(\d+)$/);
    const unitMatch = part.match(/([hm])$/i);

    if (unitMatch && !numberMatch) {
      // Sayısı olmayan birim örn: "h", "m"
      throw new Error('Geçersiz girdi: Sayı eksik');
    }

    if (!numberMatch && !unitMatch) {
      // Bilinmeyen format örn: "1abc" veya boşluk içinde başka şeyler varsa (parantez vb.)
      // Ancak prompt sadece h,m,s birimlerini belirtiyor. 
      // Güvenli olması için sadece sayı + birim yapısını bekleyelim.
      if (!part.match(/^\d+[hm]/i)) {
         throw new Error('Geçersiz girdi: Beklenmeyen format');
      }
    }

    let value = 0;
    const unitChar = (unitMatch || part.match(/[hm]/i))[1]; // Birim karakterini al

    if (!numberMatch) {
       numberMatch = part.match(/^(\d+)?/); // Sadece birim varsa sayıyı 0 kabul et ama yukarıda kontrol edildi. 
       // Düzeltme: Eğer unitMatch olduysa ve numberMatch yoksa, yukarıdaki hata fırlatılmış olmalı.
       // Bu kod bloğuna tekrar düşüyorsa, sayıya sahip olmasını sağla.
    }

    if (numberMatch) {
      value = parseInt(numberMatch[1], 10);
    } else {
      throw new Error('Geçersiz girdi: Sayı bulunamadı');
    }

    const unitIndex = units.indexOf(unitChar.toLowerCase());

    // Yanlış sıra veya tekrar eden birim kontrolü
    if (unitIndex === -1) {
      throw new Error(`Bilinmeyen birim: ${part}`);
    }

    if (unitIndex < 0 || lastUnitIndex !== -1 && unitIndex <= lastUnitIndex) {
       // Yanlış sıra (örn: m sonra h gelmesi -> index 1 sonra 0) veya tekrar eden birim
       // Sıralama: h(0), m(1), s(2). Sıra artmalı.
       if (unitIndex < lastUnitIndex + 1) {
         throw new Error('Yanlış sıra: Birimler h, m, s sırasıyla gelmelidir');
       }
    }

    // Birimi topla
    switch (unitChar.toLowerCase()) {
      case 'h': value *= 3600; break;
      case 'm': value *= 60; break;
      case 's': /* zaten saniye */ break;
      default: throw new Error('Bilinmeyen birim');
    }

    totalSeconds += value;
    
    if (unitIndex !== -1) {
      lastUnitIndex = unitIndex;
    } else {
      // Eğer sadece sayı gelse ve birim yoksa, bu gereksizdir ama hata fırlatıyoruz mu? 
      // Prompt: "sayısı olmayan birim" hatası. Sayı olmadan birim gelirse yukarıdaki mantıkla yakalanıyor.
      // Ancak "2h" formatında regex ile kontrol etmemiz daha iyisi.
    }
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```
